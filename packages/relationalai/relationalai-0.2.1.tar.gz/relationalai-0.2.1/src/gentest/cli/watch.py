import ast
import json
import os
import re
import sys
import tempfile
import time
from functools import wraps
from typing import Any, Callable, Iterable
from colorama import Style
from prompt_toolkit.enums import EditingMode
import hupper
from prompt_toolkit import PromptSession
import pytest

from gentest.util import PROJECT_DIR
from gentest.validate.errors import GenException
from gentest.harness.database import expand_short_path
from gentest.cli.collect_failures import FailInfo, FailureCollectorPlugin
from gentest.cli.collect_tests import collect_tests, pytest_node_fn, pytest_node_name
from gentest.cli.repro import Shareable, encode_shareable, export_ir, export_pyrel, get_example, get_fn_file, reproduce, reproduce_blob



class State:
    should_die = False
    session_start: float
    runs = 0
    repro_target: str|None = None
    export_ir: str|None = None
    export_pyrel: str|None = None

    def __init__(self, state_file_path: str):
        self.state_file_path = state_file_path

    def get(self, key: str, default: Any):
        return vars(self).get(key, default)

    def load(self):
        with open(self.state_file_path, 'r') as state_file:
            state = json.load(state_file)
            for key, value in state.items():
                setattr(self, key, value)

    def dump(self):
        state = {k: v for k, v in vars(self).items() if not callable(v)}
        with open(self.state_file_path, 'w') as state_file:
            json.dump(state, state_file)

    def has_exports(self):
        return bool(self.export_pyrel or self.export_ir)

    def do_exports(self):
        if self.repro_target and self.has_exports():
            ex = get_example(self.repro_target)
            if self.export_ir:
                export_ir(self.repro_target, self.export_ir, ex)
            if self.export_pyrel:
                export_pyrel(self.repro_target, self.export_pyrel, ex)

    def get_target(self) -> str:
        if not self.repro_target:
            raise Exception("No target failure for operation!")

        return self.repro_target

    def __repr__(self):
        kwargs = ", ".join(f"{k}={repr(v)}" for k, v in vars(self).items() if not callable(v))
        return f"State({kwargs})"

failure_collector = FailureCollectorPlugin()

def run_tests(state: State):
    sys.stdout.write('\r\033[K')
    sys.stdout.flush()
    print()
    print(f" RUN {state.runs} ".center(80, "#"))
    repro_target = state.get("repro_target", None)
    if repro_target:
        reproduce(repro_target)
        state.do_exports()
    else:
        pytest.main(['-s'], plugins=[failure_collector])

    state.runs += 1
    state.dump()

def get_failure(ix: int):
    failures = failure_collector.get_failures()
    if ix > len(failures) or ix < 1:
        raise ArgumentError(f"'{ix}' is not a valid failure index from the last run ({len(failures)} failure(s)).")

    return failures[ix - 1]

def failure(by: str):
    try:
        ix = int(by)
        if ix == 0:
            raise ArgumentError("Failures are 1-indexed for convenience. Try `target 1` instead.")
        return get_failure(ix)

    except ValueError:
        if not re.match(r'^[a-zA-Z0-9]+/[a-zA-Z0-9]+$', by):
            raise ArgumentError(f"{by} is not a valid failure index or path")

        key_hash, value_hash = by.split("/")
        for failure in failure_collector.get_failures():
            err = failure.error
            if isinstance(err, GenException):
                if err.key_hash and err.key_hash.startswith(key_hash) and err.value_hash().startswith(value_hash):
                    return failure

        raise ArgumentError(f"{by} does not correspond to an existing failure index or path. Try `list` to see valid options.")

def failure_path(by: str):
    try:
        ix = int(by)
        if ix == 0:
            raise ArgumentError("Failures are 1-indexed for convenience. Try `target 1` instead.")
        fail_info = get_failure(ix)
        err = fail_info.error
        if not isinstance(err, GenException):
            print(f"Provided ix '{ix}' is not a gen exception, so most repro functionality will not work with it.")
            print(str(err))
            print(type(err))
            return

        return err.hash_path()
    except ValueError:
        if not re.match(r'^[a-zA-Z0-9]+/[a-zA-Z0-9]+$', by):
            raise ArgumentError(f"{by} is not a valid failure index or path")

        try:
            by = expand_short_path(by, relative=True)
        except Exception as err:
            raise ArgumentError(f"{by} is not a valid failure index or path")
        return by

    

ArgParser = Callable[[str], Iterable[Any]]
Action = Callable[[str], Any]

class ArgumentError(Exception):
    ops: list[str]

    def __init__(self, message: str):
        super().__init__(message)
        self.ops = []
        self.message = message

    def prefix_op(self, op: str):
        self.ops.insert(0, op)
        return self

    def __str__(self):
        if self.ops:
            return f"[{' '.join(self.ops)}] {self.message}"
        return self.message


def arg_parser(parser: ArgParser):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(user_input: str):
            return func(*parser(user_input))

        help_str = getattr(parser, "__help_str", None)
        if help_str is None:
            print(f"WARN: arg parser {parser.__name__} does not have help text configured. Use @help.")
        else:
            setattr(wrapper, "__arg_help_str", help_str)
        return wrapper
    return decorator

def help(help_text: str):
    def decorator(func):
        setattr(func, "__help_str", help_text)
        return func

    return decorator

@help('')
def no_args(_: str):
    return ()

class CommandSet:
    actions: list[tuple[Iterable[str], Action]]
    call_path: list[str]

    __name__: str = "subcommand"
    __help_str: str|None = None
    __arg_help_str: str|None = None
    _ = __help_str, __arg_help_str # shut up pyright

    def __init__(self, help_str: str|None = None, name: str|None = None):
        self.actions = []
        self.call_path = []
        self.add(('h', 'help', '?'), self.print_help_action)
        self.__help_str = help_str
        self.__arg_help_str = self.get_help_str()
        setattr(self, '__name__', name)

    def __call__(self, args: str):
        try:
            self.dispatch(*self.dispatch_parser(args))
        except TypeError as err:
            if str(err).startswith("CommandSet.dispatch()"):
                print(f"{Style.BRIGHT}Missing subcommand. Valid options are:{Style.NORMAL}\n")
                self.print_help()
            else:
                raise

    def dispatch(self, op: str, args: str = ''):
        for key, action in self.actions:
            if op in key:
                try:
                    if isinstance(action, CommandSet):
                        action.call_path = self.call_path + [op]
                    action(args)
                except ArgumentError as err:
                    raise err.prefix_op(op)

                break
        else:
            print(f"{Style.BRIGHT}Unrecognized subcommand '{op}'. Valid options are:{Style.NORMAL}\n")
            self.print_help()

    def dispatch_parser(self, raw: str):
        return raw.split(maxsplit=1)

    def get_help_str(self):
        ops = '|'.join(op for (ops, _) in self.actions for op in ops)
        return f"<op: {ops}> [args...]"

    def add(self, op: str|Iterable[str], action: Action):
        if isinstance(op, str):
            op = (op,)

        self.actions.insert(-1, (op, action))
        # self.get_help_str()
        return self


    @help("Print this help text.")
    def print_help_action(self, _: str):
        return self.print_help()

    def print_help(self, indent = 0):
        pad = "    " * indent
        max_op_len = 0
        max_arg_len = 0
        op_texts = []
        arg_texts = []
        desc_texts = []
        for key, action in self.actions:
            op_text = '|'.join(key)
            if len(op_text) > max_op_len:
                max_op_len = len(op_text)
            arg_text = getattr(action, '__arg_help_str', '')
            if len(arg_text) > max_arg_len:
                max_arg_len = len(arg_text)

            op_texts.append(op_text)
            arg_texts.append(arg_text)
            desc_texts.append(getattr(action, '__help_str', action.__name__))

        for (op, arg, desc) in zip(op_texts, arg_texts, desc_texts):
            print(f"{pad}{op:<{max_op_len}}  {arg:<{max_arg_len}} -- {desc}")


def simple_kwarg_parser(kwarg_parsers: dict[str, Callable[[str], Any]]) -> ArgParser:
    help_str = ' '.join(f"<{key}: {parser.__name__}>" for key, parser in kwarg_parsers.items())
    @help(help_str)
    def parse(raw: str):
        args = raw.split()
        res = []
        expected_len = len(kwarg_parsers.keys())
        actual_len = len(args)
        if(expected_len != actual_len):
            print(f"Invalid arguments, expecting: {help_str}")
            raise ArgumentError(f"expected {expected_len} arguments, got {actual_len}.")
        for key, arg in zip(kwarg_parsers.keys(), args):
            res.append(kwarg_parsers[key](arg))

        return res
    return parse

def build_cmd_tree(state: State):
    @arg_parser(simple_kwarg_parser({"out": str}))
    @help("Export the pickled IR from the targeted failure to OUT")
    def export_ir_action(out: str):
        export_ir(state.get_target(), out)
        state.export_ir = out
        state.dump()

    @arg_parser(simple_kwarg_parser({"out": str}))
    @help("Export the emitted PyRel from the targeted failure to OUT")
    def export_pyrel_action(out: str):
        export_pyrel(state.get_target(), out)
        state.export_pyrel = out
        state.dump()

    @arg_parser(no_args)
    @help("Encode a binary blob that will allow others to reproduce the targeted failure")
    def export_blob_action():
        print(repr(encode_shareable(state.get_target())))

    @arg_parser(no_args)
    @help("Clear all active exports")
    def export_clear_action():
        state.export_ir = None
        state.export_pyrel = None
        print("Clearing active exports.")
        state.dump()

    export_cmd = (
        CommandSet("Export the example generated in the targeted failure.")
        .add(('ir', 'i'), export_ir_action)
        .add(('pyrel', 'p'), export_pyrel_action)
        .add(('blob', 'b'), export_blob_action)
        .add(('clear', 'c'), export_clear_action)
    )

    @arg_parser(simple_kwarg_parser({"target": failure_path}))
    @help("Focus the specified failure, only re-running it on change.")
    def target_action(short_path: str):
        state.repro_target = short_path
        state.dump()
        run_tests(state)

    @arg_parser(no_args)
    @help("Clear the targeted failure and any running operations like export that depend on it.")
    def clear_action():
        was_targeted = state.repro_target is not None
        state.repro_target = None
        state.export_ir = None
        state.export_pyrel = None
        state.dump()

        if was_targeted:
            run_tests(state)

    @arg_parser(no_args)
    @help("Print a short list of the accumulated failures from the last run.")
    def list_action():
        for ix, failure in enumerate(failure_collector.get_failures(), start=1):
            match failure.error:
                case GenException():
                    prefix = f"{ix}. {failure.error.short}"
                    print(f"{prefix:<80}[{failure.error.hash_path()}]")
                case _:
                    msg = str(failure.error)
                    print(f"{ix}. {msg[:75]}{'…' if len(msg) > 75 else ''}")

    @arg_parser(simple_kwarg_parser({"target": failure}))
    @help("Show details for the specified failure.")
    def show_action(failure: FailInfo):
        target = pytest_node_fn(failure.node)
        target = getattr(target, "inner", target)
        if hasattr(target, "hypothesis"):
            target = target.hypothesis.inner_test

        file = target.__code__.co_filename
        name = pytest_node_name(failure.node)
        print(f"file     {os.path.relpath(file, PROJECT_DIR)}")
        print(f"test     {name}")
        if isinstance(failure.error, GenException):
            print(f"failpath {failure.error.hash_path()}")
        print(failure.error)

    @help("<shareable: tuple>")
    def shareable_blob_parser(raw: str):
        try:
            shareable = ast.literal_eval(raw)
            if isinstance(shareable, tuple) and len(shareable) == 3:
                return shareable,
        except (ValueError, SyntaxError):
            pass

        raise ArgumentError("Argument should be in the format `('test/file/path', 'test_name', b'reproblob')`. Produce a shareable blob with `e b`")

    @arg_parser(shareable_blob_parser)
    def import_action(shareable: Shareable):
        test_path, test_name, blob = shareable
        tests = collect_tests()
        for test in tests:
            print(pytest_node_name(test), get_fn_file(pytest_node_fn(test).inner))
            if pytest_node_name(test) != test_name:
                continue
            fn = pytest_node_fn(test)
            if get_fn_file(getattr(fn, "inner", fn)) == test_path:
                break
        else:
            raise Exception(f"Unable to find specified test {test_name} in {test_path}.")

        reproduce_blob(fn, blob)

    @arg_parser(no_args)
    @help("Quit gentest.")
    def quit_action():
        print("Goodbye!")
        state.should_die = True
        state.dump()

    return (
        CommandSet("Operate on the failing tests.")
        .add(('target', 't'), target_action)
        .add(('clear', 'c'), clear_action)
        .add(('export', 'e'), export_cmd)
        .add(('list', 'l'), list_action)
        .add(('show', 's'), show_action)
        .add(('import', 'i'), import_action)
        .add(('quit', 'q'), quit_action)
    )

def run_repl(state: State):
    session = PromptSession()
    cmd = build_cmd_tree(state)
    while True:
        try:
            # Prompt for user input
            user_input: str = session.prompt('> ', editing_mode=EditingMode.EMACS)
            if not user_input.strip():
                cmd.print_help()
            else:
                cmd(user_input)
                if state.should_die:
                    break
        except ArgumentError as err:
            print(str(err))
        except (EOFError, KeyboardInterrupt):
            print("Goodbye!")
            break


# Main function to start test watching and interactive CLI
def run(state_file_path: str|None = None):
    owns_state_file = False
    if state_file_path is None:
        _, state_file_path = tempfile.mkstemp(prefix='gentest_cli_state_', suffix='.json')
        with open(state_file_path,  'w') as state_file:
            json.dump({'session_start': time.time()}, state_file)
            owns_state_file = True

    try:
        reloader: Any = hupper.start_reloader("gentest.cli.watch.run", worker_args=(state_file_path,), verbose=0)

        state = State(state_file_path)
        state.load()
        run_tests(state)
        run_repl(state)

        # Violently kill the parent process by feeding it an unexpected message, since hupper lacks this functionality :/
        reloader.pipe.send("exit")
        sys.exit(0)

    except RuntimeError as err:
        if not str(err).endswith("('received unknown control signal', 'exit')"):
            raise
    finally:
        try:
            if owns_state_file:
                os.remove(state_file_path)
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    run()
