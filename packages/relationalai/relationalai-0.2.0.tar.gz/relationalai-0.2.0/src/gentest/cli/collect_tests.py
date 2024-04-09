from io import StringIO
import sys
from typing import Any
from _pytest.nodes import Node
import pytest

class TestCollectorPlugin:
    def __init__(self):
        self.items: list[Node] = []

    def pytest_collection_modifyitems(self, items):
        for item in items:
            self.items.append(item)

_cached_tests: list[Node]|None = []

def collect_tests(force_recollect = False):
    global _cached_tests
    if force_recollect:
        _cached_tests = None
    if _cached_tests:
        return _cached_tests

    collector = TestCollectorPlugin()
    buf = StringIO()
    buf.isatty = lambda: True
    prev_stdout = sys.stdout
    sys.stdout = buf
    try:
        pytest.main(["--collect-only", "-q"], plugins=[collector])
    finally:
        sys.stdout = prev_stdout
        contents = buf.getvalue()
        if "ERROR" in contents:
            print("Failed to collect tests, see reason below:")
            print(contents)

    return collector.items

def pytest_node_fn(node: Node):
    n: Any = node
    assert callable(n._obj)
    return n._obj

def pytest_node_name(node: Node):
    n: Any = node
    return n.originalname

if __name__ == "__main__":
    items = collect_tests()
    print("COLLECTED")
    for item in items:
        fn = pytest_node_fn(item)
        print(item, getattr(fn, "__key_hash", None))
