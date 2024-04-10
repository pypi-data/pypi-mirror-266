from typing import Any, Iterable, Sequence

import pandas as pd
from railib import api

from relationalai.dsl import safe_symbol
from relationalai.errors import RelQueryError

#-------------------------------------------------------------------------------
# Emitting
#-------------------------------------------------------------------------------

class Char(str):
    def __new__(cls, value):
        if value is None:
            raise ValueError("Char cannot be None")
        if len(value) != 1:
            raise ValueError("A Char must be a single character")
        return str.__new__(cls, value)

def emit_literal(v: Any):
    """Emit `v` as its equivalent literal representation in rel."""
    if isinstance(v, Char):
        sanitized = v.replace("'", "\\'")
        return f"'{sanitized}'"
    if isinstance(v, str):
        sanitized = v.replace('"', '\\"').replace("%", "\\%")
        return f'"{sanitized}"'
    if isinstance(v, tuple):
        return ", ".join(emit_literal(item) for item in v)
    return v

def emit_nested_relation(prefix: str, obj: dict|None = None, keys: Iterable[str]|None = None, raw = False) -> str:
    """Emit a set of defs encoding `obj` in GNF on `prefix`."""
    obj = obj or {}
    result = ""
    for k in keys or obj.keys():
        v = obj.get(k, None)
        if v is not None:
            result += f"def {prefix}[{safe_symbol(k)}] = {emit_literal(v) if not raw else v}\n"
    return result

#-------------------------------------------------------------------------------
# Result Handling
#-------------------------------------------------------------------------------

_known_problems: list[Any] = []
def ignore_known_problems(problems: Sequence[Any]):
    """Filter out issues already in `problems` when checking responses for rel problems."""
    global _known_problems
    _known_problems.clear()
    _known_problems.extend(problems)

def assert_no_problems(res: api.TransactionAsyncResponse):
    """Throw a vaguely-readable exception if rel problems were reported with the given transaction."""
    new_problems = []
    for problem in res.problems:
        if problem not in _known_problems:
            new_problems.append(problem)

    if new_problems:
        raise RelQueryError(new_problems)

def maybe_scalarize(v):
    if getattr(v, "__len__", None) and len(v) == 1:
        return v[0]
    return v

def process_gnf_results(gnf: Sequence, *key_names: str):
    """Process GNF results into a nested object keyed by the key(s) in `key_names`"""
    assert len(key_names) > 0, "Must supply a name for the GNF key(s)"
    key_size = len(key_names)

    obj = {}

    for rel in gnf:
        sig = rel["relationId"].split("/")
        if sig[1] != ":output":
            continue

        table: pd.DataFrame = rel["table"].to_pandas()

        key_cols = table.columns[0:key_size]

        for _, row in table.iterrows():
            raw_keys = tuple(row[col] for col in key_cols)
            keys = maybe_scalarize(raw_keys)
            vals = [row[col] for col in table.columns[key_size:]]

            entry = obj.setdefault(keys, {k: v for k, v in zip(key_names, raw_keys)})

            cur = 4
            field = sig[cur - 2][1:]
            while len(sig) > cur and sig[cur][0] == ":":
                entry = entry.setdefault(field, {})
                field = sig[cur][1:]
                cur += 2
            entry[field] = maybe_scalarize(vals)

    return obj
