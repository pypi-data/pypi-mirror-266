#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import argparse
import os
import re
from typing import Any, Callable
import argcomplete
from gentest.cli.repro import encode, reproduce, export_ir, export_pyrel
from gentest.cli.run_tests import run_tests
from gentest.cli.watch import run as watch

subparsers: dict[argparse.ArgumentParser, argparse._SubParsersAction] = {}

def add_command(name: str, help: str, args: dict[str, dict], parent:argparse.ArgumentParser|None=None, action: Callable[..., Any]|None = None, allow_unknown = False):

    if parent:
        if parent not in subparsers:
            subparsers[parent] = parent.add_subparsers(dest='subcommand', help=f'Sub-commands for {parent.prog}')
        subparser = subparsers[parent]
        parser = subparser.add_parser(name, help=help)
    else:
        parser = argparse.ArgumentParser(name, description=help)

    for arg_name, arg_info in args.items():
        parser.add_argument(arg_name, **arg_info)

    # Store the action directly in the parser
    if action:
        parser.set_defaults(func=action)

    if allow_unknown:
        parser.set_defaults(allow_unknown=allow_unknown)

    return parser

def to_short_path(value) -> bool:
    if not re.match(r'^[a-zA-Z0-9]+/[a-zA-Z0-9]+$', value):
        raise argparse.ArgumentTypeError(f"'{value}' is not in the format <key_hash>/<value_hash>")
    return value

def to_file_path(path):
    if not os.path.normpath(path) == path:
        raise argparse.ArgumentTypeError(f"'{path}' contains invalid characters for a file path")

    return path



def main():
    parser = add_command('gentest', 'Development tool for generative test suite.', {})

    short_path = {'help': 'Path to the failing example.', 'type': to_short_path}
    out = {'help': 'Output file path to write to.', 'type': to_file_path}
    ix = {'help': 'Which argument of the test should be emitted', 'type': int, 'default': 0}

    add_command('test', 'Run the test suite, passing args through to pytest.', {}, parent=parser, action=run_tests, allow_unknown=True)
    add_command('watch', 'Run the development tool, validating changes as they get made.', {}, parent=parser, action=watch)
    add_command('encode-failure', 'Encode a failure as a base64 string.', {'short_path': short_path}, parent=parser, action=encode)
    add_command('reproduce', 'Reproduce a failing test case.', {'short_path': short_path}, parent=parser, action=reproduce)

    export_parser = add_command('export', 'Export utilities for debugging.', {}, parent=parser)
    add_command('ir', 'Export the intermediate representation for debugging.', {'short_path': short_path, 'out': out}, parent=export_parser, action=export_ir)
    add_command('pyrel', 'Export the Python DSL code for debugging.', {'short_path': short_path, 'out': out, '--ix': ix}, parent=export_parser, action=export_pyrel)

    argcomplete.autocomplete(parser)

    # args = parser.parse_args()
    args, unknown_args = parser.parse_known_args()
    if hasattr(args, 'func'):
        kwargs = {**vars(args)}
        kwargs.pop('func')
        kwargs.pop('allow_unknown', None)
        kwargs.pop('subcommand', None)
        if getattr(args, 'allow_unknown', False):
            kwargs['unknown_args'] = unknown_args
        elif len(unknown_args):
            raise argparse.ArgumentError(None, f"Specified subcommand doesn't consume the following flags: {', '.join(unknown_args)}")
        args.func(**kwargs)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
