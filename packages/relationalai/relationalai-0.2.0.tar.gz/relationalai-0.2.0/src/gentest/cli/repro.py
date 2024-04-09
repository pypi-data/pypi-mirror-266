import inspect
import os
import pickle
import sys
from typing import Any, Callable, Type
import hypothesis
from hypothesis.core import encode_failure
from hypothesis.errors import DidNotReproduce
from relationalai import metamodel as mm
from gentest.util import PROJECT_DIR
from gentest.harness.database import HYPO_DB_PATH, expand_short_path, get_conjecture_data
from gentest.validate.errors import GenException
from gentest.cli.collect_tests import collect_tests, pytest_node_fn, pytest_node_name


from gentest.emit import DocumentEmitter

def get_fn_file(fn, relative_to = os.path.join(PROJECT_DIR, "..")):
    file = sys.modules[fn.__module__].__file__
    return os.path.relpath(file, relative_to) if file else None

def get_test_for(repro_path: str):
    if HYPO_DB_PATH  in repro_path:
        repro_path = os.path.relpath(repro_path, HYPO_DB_PATH)
    key_hash = repro_path[0:repro_path.find("/")]
    tests = collect_tests()
    for test in tests:
        fn = pytest_node_fn(test)
        cur_key = getattr(fn, "__key_hash", "")
        if cur_key.startswith(key_hash):
            break
    else:
        raise Exception("Unable to find a matching test for the given key hash.")

    return (test, fn)


def get_failure_repro_blob(conjecture_data: bytes):
    return encode_failure(conjecture_data)

def get_generated_example_for_fn(blob: bytes, fn: Any) -> tuple[tuple, list[Any]]:
    params = inspect.signature(fn.inner.hypothesis.inner_test).parameters
    types = [param.annotation if param.annotation else "Any" for param in params.values() if param.name != "data"]

    args = ()
    def collect_args(**kwargs):
        nonlocal args
        args = tuple(kwargs[param] for param in params.keys() if param != "data")

    prev_inner = fn.inner.hypothesis.inner_test
    fn.inner.hypothesis.inner_test = collect_args
    try:
        fn()
    except Exception:
        pass
    finally:
        fn.inner.hypothesis.inner_test = prev_inner

    return (args, types)

def encode(short_path: str):
    repro_path = expand_short_path(short_path, HYPO_DB_PATH)
    print(f"Retrieving repro input from {os.path.relpath(repro_path, os.path.dirname(PROJECT_DIR))}")
    data = get_conjecture_data(repro_path)
    blob = get_failure_repro_blob(data)
    print(f"Reproduce the failure by adding the following decorator to the test case: `@reproduce_failure(\"{hypothesis.__version__}\", {repr(blob)})`")

Shareable = tuple[str, str, bytes]

def encode_shareable(short_path: str):
    repro_path = expand_short_path(short_path, HYPO_DB_PATH)
    print(f"Retrieving repro input from {os.path.relpath(repro_path, os.path.dirname(PROJECT_DIR))}")
    data = get_conjecture_data(repro_path)
    blob = get_failure_repro_blob(data)
    test, fn = get_test_for(repro_path)
    return (get_fn_file(fn.inner), pytest_node_name(test), blob)

def reproduce(short_path: str):
    repro_path = expand_short_path(short_path, HYPO_DB_PATH)
    print(f"Retrieving repro input from {os.path.relpath(repro_path, os.path.dirname(PROJECT_DIR))}")
    data = get_conjecture_data(repro_path)
    blob = get_failure_repro_blob(data)
    test, fn = get_test_for(repro_path)
    print(f"Reproducing failure for test {pytest_node_name(test)} in {get_fn_file(fn.inner)} with input {repr(blob)}")
    return reproduce_blob(fn, blob)

def reproduce_blob(test_fn: Callable, blob: bytes):
    inner = test_fn.inner
    try:
        test_fn.inner = hypothesis.reproduce_failure(hypothesis.__version__, blob)(test_fn.inner)
        test_fn(False)
    except GenException as err:
        print(err.pprint())
    except DidNotReproduce:
        print()
        print("✨ Could not reproduce failure. You fixed it! ✨")
    finally:
        test_fn.inner = inner
        del test_fn.inner._hypothesis_internal_use_reproduce_failure

def get_example_inputs(short_path: str):
    repro_path = expand_short_path(short_path, HYPO_DB_PATH)
    print(f"Retrieving repro input from {os.path.relpath(repro_path, os.path.dirname(PROJECT_DIR))}")
    data = get_conjecture_data(repro_path)
    blob = get_failure_repro_blob(data)
    test, fn = get_test_for(repro_path)
    print(f"Generating input for {pytest_node_name(test)} in {get_fn_file(fn.inner)} from {repr(blob)}")
    args, types = get_generated_example_for_fn(blob, fn)
    return args, types

def get_example(short_path: str, ix = 0) -> tuple[Any, Type]:
    inputs = get_example_inputs(short_path)
    return inputs[0][ix], inputs[1][ix]

def export_inputs(short_path: str, out: str):
    args, types = get_example_inputs(short_path)
    print(f"Writing repro to {out} as tuple of ({', '.join(t.__name__ for t in types)})")
    with open(out, "wb") as file:
        pickle.dump(args, file)

def export_ir(short_path: str, out: str, example: tuple[Any, Type]|None = None, ix = 0):
    if not example:
        example = get_example(short_path, ix)
    value, arg_type = example
    print(f"Writing {arg_type.__name__} to {out}")
    with open(out, "wb") as file:
        pickle.dump(value, file)

def emit_task(task: mm.Task):
    doc = DocumentEmitter()
    doc.rule(task)
    return doc.stringify().strip()

EMITTERS = {
    mm.Task: emit_task
}

def export_pyrel(short_path: str, out: str, example: tuple[Any, Type]|None = None, ix = 0):
    if not example:
        example = get_example(short_path, ix)
    value, arg_type = example
    print(f"Emitting pyrel for {arg_type.__name__}")
    if arg_type not in EMITTERS:
        raise Exception(f"Failed to emit pyrel for {arg_type.__name__}, no registered emitter.")

    emitter = EMITTERS[arg_type]

    emitted = emitter(value)
    print(f"Writing pyrel to {out}")
    with open(out, "w") as file:
        file.write(emitted)
