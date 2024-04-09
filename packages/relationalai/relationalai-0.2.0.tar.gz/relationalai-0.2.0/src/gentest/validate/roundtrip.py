import time
from typing import Any, Callable, Sequence
from colorama import Style
from gentest.harness.database import get_test_hash
from gentest.util import condense_traceback, fmt_h2, fmt_indented, stringify_blocks
from hypothesis.internal.observability import TESTCASE_CALLBACKS
from relationalai.clients.test import Document, Install, Query, proxied_clients
from gentest.validate.diff import diff_to_str
from gentest.emit import DocumentEmitter
from gentest.validate.mapping import map_document_ids

from gentest.validate.errors import GenException

#===============================================================================
# Decorator
#===============================================================================

def roundtripper(fn: Any, print_given_args = False):
    key_hash = get_test_hash(fn)
    started: float = 0
    runs: int = 0

    if not print_given_args:
        fn._hypothesis_internal_print_given_args = False

    def tap_debug_logs(value: Any):
        if value["type"] == "test_case":
            nonlocal runs
            nonlocal started
            runs += 1
            if runs % 100 == 0:
                end = time.time_ns()
                elapsed = (end - started) / 1000000
                print(f"{runs} tasks tested. {elapsed:.2f}ms elapsed. Avg {elapsed / runs:.4f}ms per task")
                # pprint.pprint(value)

    def wrapper(debug = False):
        __tracebackhide__ = True
        nonlocal started
        nonlocal runs
        started = time.time_ns()
        runs = 0

        if debug:
            TESTCASE_CALLBACKS.append(tap_debug_logs)
            try:
                wrapper.inner()
            except Exception as err:
                print(fmt_err(err, None, key_hash))
            finally:
                TESTCASE_CALLBACKS.remove(tap_debug_logs)

            end = time.time_ns()
            elapsed = (end - started) / 1000000
            if runs == 0:
                runs = 1
            print(f"{runs} tasks tested. {elapsed:.2f}ms elapsed. Avg {elapsed / runs:.4f}ms per task")
        else:
            try:
                wrapper.inner()
            except Exception as err:
                setattr(err, "key_hash", key_hash)
                raise
            # try:
            #     wrapper.inner()
            # except ExceptionGroup as err:
            #     raise Exception(fmt_err(err, None, key_hash)) from None
            # except GenException as err:
            #     raise Exception(fmt_err(err, None, key_hash)) from None

    wrapper.__key_hash = key_hash
    wrapper.inner = fn
    return wrapper

def fmt_errs(errs: Sequence[Exception], key_hash: str, indent = 0):
    pad = "  " * indent
    segments = [f"{pad}{Style.BRIGHT}{len(errs)} exceptions found:{Style.NORMAL}"]
    ix = 0
    for err in errs:
        segments.append(fmt_err(err, f"{ix + 1:02}", key_hash, indent))
        ix += 1

    return "\n\n".join(segments)

def fmt_err(err: Exception, label: str|None, key_hash: str, indent = 0) -> str:
    pad = "  " * indent
    match err:
        case ExceptionGroup():
            return fmt_errs(err.exceptions, key_hash, indent)
        case GenException():
            body = err.reify().long or ""
            cut_ix = body.find("\n")
            body = body[cut_ix + 1:]

            return f"{pad}{fmt_h2(err.short, err.hash_path(key_hash), indent=indent)}\n{fmt_indented(body, indent)}"
        case _:
            return f"{pad}{fmt_h2(label, indent=indent)}\n{pad}{Style.BRIGHT}{str(err)}{Style.RESET_ALL}\n{fmt_indented(condense_traceback(err), indent + 1)}\n"


#===============================================================================
# Exec
#===============================================================================

def return_document(doc: Document):
    return doc

def drain_proxied_clients():
    proxies = proxied_clients[:]
    proxied_clients.clear()
    return proxies

def get_proxied_client():
    proxies = drain_proxied_clients()
    assert len(proxies) == 1
    return proxies[0]

def exec_and_run_callback(code: str, callback: Callable[..., Any]|None, *args: Any, ns:dict|None = None):
    if callback is None:
         callback = return_document

    try:
        exec(code, ns, None)
        return callback(get_proxied_client(), *args)
    finally:
        drain_proxied_clients()

#===============================================================================
# From code
#===============================================================================

def roundtrip_from_pyrel_code(code: str):
    # print("ORIG" + "="*76)
    # print(code)
    exec_and_run_callback(code, emit_and_compare)

def emit_and_compare(executor: Document):
    doc = DocumentEmitter()
    for block in executor.blocks:
        match block:
            case Install():
                if block.name != "pyrelstd":
                    doc.rule(block.task)
            case Query():
                doc.query(block.task)

    code2 = doc.stringify()

    print("EMIT" + "="*76)
    print(code2)

    exec_and_run_callback(code2, compare_metamodels, executor)

def compare_metamodels(new: Document, old: Document):
    map_document_ids(old, new)
    old_str = stringify_blocks(old.blocks)
    new_str = stringify_blocks(new.blocks)
    # print("OLD" + "="*77)
    # print(old_str)
    # print("NEW" + "="*77)
    # print(new_str)
    print("DIFF" + "="*76)
    print(diff_to_str(old_str, new_str))

