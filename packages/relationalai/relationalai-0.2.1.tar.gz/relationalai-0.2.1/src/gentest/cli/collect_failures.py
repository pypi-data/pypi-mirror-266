import datetime
from _pytest.nodes import Node
import pytest

class FailInfo:
    def __init__(self, run: int, node: Node, error: Exception):
        self.run = run
        self.node = node
        self.error = error
        self.when = datetime.datetime.now()

class FailureCollectorPlugin:
    def __init__(self):
        self.failures: list[FailInfo] = []
        self.run_counter = 0

    @pytest.hookimpl(tryfirst=True)
    def pytest_sessionstart(self, session):
        self.failures.clear()
        self.run_counter += 1

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_makereport(self, item, call):
        if call.when == "call" and call.excinfo is not None:
            excinfo: pytest.ExceptionInfo = call.excinfo
            err = excinfo.value
            match err:
                case ExceptionGroup():
                    key_hash = getattr(err, 'key_hash', None)
                    for sub_err in err.exceptions:
                        if key_hash:
                            setattr(sub_err, 'key_hash', key_hash)

                        self.failures.append(FailInfo(self.run_counter, item, sub_err))
                case _:
                    self.failures.append(FailInfo(self.run_counter, item, err))

    def get_failures(self):
        return self.failures
