from _pytest._io.wcwidth import wcswidth
from _pytest.terminal import TerminalReporter
from gentest.util import condense_traceback
import pytest

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    term: TerminalReporter = item.config.pluginmanager.getplugin("terminalreporter")
    write_status(term)

    yield


def write_status(term: TerminalReporter):
    cur_line = term._tw._current_line
    prefix = trim_suffix(cur_line)
    w = wcswidth(prefix) # term._width_of_current_line
    term._tw.fullwidth - w - 1

    term.rewrite("\r" + prefix, erase=True)
    # term.write(msg.rjust(fill), flush=True, green=True)

def trim_suffix(line: str):
    ix = line.find("   ")
    return line if ix == -1 else line[0:ix]



def custom_repr_failure(self, excinfo: pytest.ExceptionInfo, style=None):
    err = excinfo.value
    match err:
        case Exception():
            return str(err) + "\n\n" + condense_traceback(err)
        case _:
            raise err
    # return str(excinfo.value)
    # print("hi", excinfo)

pytest.Function.repr_failure = custom_repr_failure
