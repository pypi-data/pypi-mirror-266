from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar
from colorama import Back, Fore, Style
from gentest.harness.database import get_short_path, get_value_hash
from gentest.util import condense_traceback, decorate, fmt_h3, fmt_indented, fmt_lines, fmt_styled_lines, get_last_exception_entry
from hypothesis.errors import _Trimmable

T = TypeVar("T")

Formatter = Callable[[T], str]

ERROR_DECORATION = decorate(Back.RED, Back.RESET, Fore.RED + Style.BRIGHT, Style.NORMAL + Fore.RESET)

#===============================================================================
# Errors
#===============================================================================

class LazyException(Exception, ABC):
    def __init__(self, short: str):
        super().__init__(short)
        self.short = short
        self.long = None
        self.message = short

    @abstractmethod
    def pprint(self) -> str:
        pass

    def reify(self):
        if not self.long:
            self.long = self.pprint()
            self.message = self.long

        return self

    def __str__(self):
        return self.message

class GenException(LazyException):
    conjecture: bytes

    label: str|None
    key_hash: str|None

    def __init__(self, short: str, conjecture: bytes, key_hash: str|None = None):
        super().__init__(short)
        self.conjecture = conjecture
        self.key_hash = key_hash

    def annotate(self, label: str|None, key_hash: str|None):
        self.label = label
        self.key_hash = key_hash

    def value_hash(self):
        return get_value_hash(self.conjecture)

    def hash_path(self, key_hash: str|None = None):
        if not key_hash:
            key_hash = self.key_hash

        if not key_hash:
            print("Cannot get hash path without a provided or annotated key hash.")
            return ""

        return get_short_path(key_hash, self.value_hash())

class RoundtripError(GenException, Generic[T], ABC):
    description: str
    expected: T

    def __init__(self, expected: T, conjecture: bytes):
        name = self.__class__.__name__
        short = f"{name}: {self.description}"
        super().__init__(short, conjecture)
        self.expected = expected

    @abstractmethod
    def body(self) -> list[str]:
        pass

    def pprint(self):
        return "\n".join([
            f"{Style.BRIGHT}{self.short}{Style.RESET_ALL}",
            *self.body()
        ])

class WrappedError(RoundtripError[T]):
    description = "An unexpected error occurred while running the test."

    def __init__(self, expected: T, conjecture: bytes, err: Exception, fmt: Formatter[T] = str):
        super().__init__(expected, conjecture)
        self.err = err
        self.fmt = fmt

    def body(self):
        pad = "    "
        return [
            fmt_h3("CAUSE", indent=1),
            fmt_indented(str(self.err) + ("\n" + condense_traceback(self.err)), 3),
            fmt_h3("MODEL", indent=1),
            fmt_lines(self.fmt(self.expected), pad)]

class EmitError(RoundtripError[T]):
    description = "Failed to emit code for model."

    def __init__(self, expected: T, conjecture: bytes, err: Exception, fmt: Formatter[T] = str):
        self.description = f"Failed to emit code for {expected.__class__.__name__}."
        super().__init__(expected, conjecture)
        self.err = err
        self.fmt = fmt

    def body(self):
        pad = "    "
        return [
            fmt_h3("CAUSE", indent=1),
            fmt_indented(str(self.err) + ("\n" + condense_traceback(self.err)), 4),
            fmt_h3("MODEL", indent=1),
            fmt_lines(self.fmt(self.expected), pad)]

class ExecError(RoundtripError[T]):
    description = "Failed to execute emitted PyRel."

    def __init__(self, expected: T, conjecture: bytes, code: str, err: Exception, fmt: Formatter[T] = str):
        super().__init__(expected, conjecture)

        self.code = code
        self.err = err
        self.fmt = fmt

        filename, err_line_ix, _ = get_last_exception_entry(err)
        if filename == "<string>":
            self.err_line_ix = err_line_ix
        else:
            self.err_line_ix = None

    def body(self):
        pad = "    "
        return [
            fmt_h3("CAUSE", indent=1),
            fmt_indented(str(self.err) + ("\n" + condense_traceback(self.err) if self.err_line_ix is None else ""), 4),
            fmt_h3("MODEL", indent=1),
            fmt_lines(self.fmt(self.expected), pad),
            fmt_h3("PYREL", indent=1),
            fmt_styled_lines(self.code, {self.err_line_ix: ERROR_DECORATION}, pad)]

class DiffError(RoundtripError[T]):
    def __init__(self, expected: T, conjecture: bytes, code: str, actual: T, diff: str):
        self.description = f"{expected.__class__.__name__} diverged from original."
        super().__init__(expected, conjecture)
        self.code = code
        self.actual = actual
        self.diff = diff

    def body(self):
        pad = "  "
        return [
            fmt_h3("DELTA", indent=0),
            fmt_lines(self.diff, pad),
            fmt_h3("PYREL", indent=0),
            fmt_lines(self.code, pad)]


def reify(err: Exception, key_hash: str) -> Exception:
    match err:
        case ExceptionGroup():
            for child in err.exceptions:
                reify(child, key_hash)
            return err
        case GenException():
            err.annotate(None, key_hash)
            return err.reify()
        case _Trimmable():
            err.__traceback__ = None
            return err
        case _:
            return err
