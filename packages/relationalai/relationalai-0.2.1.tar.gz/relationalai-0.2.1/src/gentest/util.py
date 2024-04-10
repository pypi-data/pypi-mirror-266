import functools
import os
import sys
import traceback
from typing import Callable, TypeVar
from colorama import Style
from hypothesis import strategies as gen
from relationalai import metamodel as mm
import relationalai
from relationalai.clients.test import Install, Query
import gentest


T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

GENTEST_ROOT_DIR = os.path.dirname(gentest.__file__)
PYREL_ROOT_DIR = os.path.dirname(relationalai.__file__)
PROJECT_DIR = os.path.dirname(os.path.dirname(PYREL_ROOT_DIR))

# Check if we're in a virtual environment
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    # We're in a virtual environment
    VENV_MODULE_DIR = os.path.join(sys.prefix, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')
else:
    # Not in a virtual environment
    VENV_MODULE_DIR = None

#===============================================================================
# Exception
#===============================================================================

def get_last_exception_entry(exception: Exception) -> tuple[str, int, str]:
    # Extract the traceback from the exception object
    tb = traceback.extract_tb(exception.__traceback__)
    # Get the last call before the exception was raised
    filename, lineno, _, text = tb[-1]
    return filename, lineno, text

def condense_traceback(exception: Exception):
    tb = traceback.extract_tb(exception.__traceback__)
    max_prefix_size = 0
    prefixes: list[str] = []
    linenos: list[int] = []
    messages: list[str] = []
    for filename, lineno, name, text in tb:
        prefix = f"{condense_path(filename)} in {name}"
        if prefix.startswith("_pytest") or prefix.startswith("pluggy"):
            continue

        if len(prefix) > max_prefix_size:
            max_prefix_size = len(prefix)
        prefixes.append(prefix)
        linenos.append(lineno)
        messages.append(text.strip())

    return "\n".join([f"{Style.DIM}{prefix: <{max_prefix_size}} {lineno: >4} |{Style.RESET_ALL} {msg}" for prefix, lineno, msg in zip(prefixes, linenos, messages)])

#===============================================================================
# String
#===============================================================================

UNDERLINE = "\033[4m"
END_UNDERLINE = "\033[0m"

def fmt_boxed(msg: str, style: str = "", box_style: str = ""):
    return f"{box_style}[{style} {msg} {box_style}]"

def fmt_header(start: str|None = None, end: str|None = None, demarc: str = "-", indent = 0, line_width = 80):
    used = 2 * indent
    parts: list[str] = ['  ' * indent, Style.DIM]
    if start:
        used += len(start) + 4 # for box
    if end:
        used += len(end) + 4 # for box

    if start:
        parts.append(fmt_boxed(start, Style.NORMAL, Style.DIM))
        parts.append(Style.NORMAL)

    interstitial = demarc * (line_width - used)
    parts.append(f"{Style.DIM}{interstitial}{Style.NORMAL}")
    if end:
        parts.append(fmt_boxed(end, Style.NORMAL, Style.DIM))
        parts.append(Style.NORMAL)

    return "".join(parts)

def fmt_h1(start: str|None = None, end: str|None = None, line_width = 80, indent = 0):
    return fmt_header(start, end, "#", line_width=line_width, indent=indent)

def fmt_h2(start: str|None = None, end: str|None = None, line_width = 80, indent = 1):
    return fmt_header(start, end, "=", indent=indent, line_width=line_width)

def fmt_h3(start: str|None = None, end: str|None = None, line_width = 80, indent = 2):
    return fmt_header(start, end, "-", indent=indent, line_width=line_width)

def fmt_indented(msg: str, indent = 0):
    if indent == 0:
        return msg

    pad = "  " * indent
    return "\n".join(f"{pad}{line}" for line in msg.splitlines())

def fmt_unindented(msg: str, indent: int|None = None):
    if indent is None:
        drop = len(msg) - len(msg.lstrip())
    else:
        drop = indent * 2

    if drop == 0:
        return msg

    return "\n".join(f"{line[drop:]}" for line in msg.splitlines())

def fmt_lines(text: str, prefix: str = ""):
    return "\n".join(
        f"{prefix}{Style.DIM}{ix + 1: >5} |{Style.RESET_ALL} {line}"
        for (ix, line) in enumerate(text.rstrip().splitlines()))

Decoration = tuple[str, str, str, str]
def decorate(gutter_pre: str = Style.DIM, gutter_post: str = Style.RESET_ALL, line_pre: str = "", line_post: str = ""):
    return (gutter_pre, gutter_post, line_pre, line_post)

DEFAULT_DECORATION = decorate()
def fmt_styled_lines(text: str, decorations: dict[int|None, Decoration], prefix: str = ""):
    def deco(ix: int, slot: int):
        return decorations.get(ix, DEFAULT_DECORATION)[slot]

    return "\n".join(
        f"{prefix}{deco(ix, 0)}{ix: >5} |{deco(ix, 1)}{deco(ix, 2)} {line}{deco(ix, 3)}"
        for (ix, line) in enumerate(text.rstrip().splitlines(), start=1))



def condense_path(filename: str):
    if VENV_MODULE_DIR and filename.startswith(VENV_MODULE_DIR):
        return os.path.relpath(filename, VENV_MODULE_DIR)
    if filename.startswith(PROJECT_DIR):
        return os.path.relpath(filename, PROJECT_DIR)
    return filename

#===============================================================================
# Dicts
#===============================================================================

def invert_dict(original: dict[K, V]) -> dict[V, list[K]]:
    inverted = {}
    for k, v in original.items():
        inverted.setdefault(v, []).append(k)

    return inverted

#===============================================================================
# Functions
#===============================================================================

def wraps(inner_fn: Callable):
    def apply_wrap(wrapper: Callable):
        wrapped = functools.wraps(inner_fn)(wrapper)
        for attr in dir(inner_fn):
            if not attr.startswith("__"):
                setattr(wrapped, attr, getattr(inner_fn, attr))

        return wrapped

    return apply_wrap




#===============================================================================
# Generation Strategies
#===============================================================================

@gen.composite
def gen_partitions(draw: gen.DrawFn, items: list[T]) -> tuple[dict[T, int], int]:
    shuffled = draw(gen.permutations(items))

    mapping: dict[T, int] = {}

    cursor = 0
    count = len(shuffled)
    group_ix = 0
    while cursor < count:
        size = draw(gen.integers(min_value=1, max_value=count - cursor))
        for ix in range(size):
            v = shuffled[cursor + ix]
            mapping[v] = group_ix
        cursor += size
        group_ix += 1

    return mapping, group_ix

#===============================================================================
# Metamodel
#===============================================================================

anon_printer = mm.Printer(unnamed_vars=True)
def fmt_task(task: mm.Task) -> str:
    anon_printer.indent = 0
    return anon_printer.print(task)


def stringify_blocks(blocks: list[Query|Install]) -> str:
    chunks: list[str] = []

    ix = 0
    for block in blocks:
        match block:
            case Install():
                if block.name != "pyrelstd":
                    name = block.name or "None"
                    chunks.append(name + "-"*(80 - len(name)))
                    chunks.append(fmt_task(block.task))
            case Query():
                name = f"query{ix}"
                chunks.append(name + "-"*(80 - len(name)))
                chunks.append(fmt_task(block.task))
                ix += 1

    return "\n".join(chunks)
