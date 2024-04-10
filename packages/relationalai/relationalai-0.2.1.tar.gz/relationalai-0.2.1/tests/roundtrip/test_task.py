from gentest import fixtures
from gentest.gen.context import fixture
from gentest.gen.scope import GenScope
from gentest.validate.diff import diff_to_str
from hypothesis import settings, given, strategies as gen
from hypothesis.internal.conjecture.data import ConjectureData
from relationalai import metamodel as mm
from relationalai.clients.test import Executor

from gentest.emit import DocumentEmitter
from gentest.validate.mapping import map_task_ids, normalize_expected_task
from gentest.util import Query, fmt_task
from gentest.harness.database import HYPO_DB
from gentest.gen.task import gen_task
from gentest.validate.errors import RoundtripError, EmitError, ExecError, DiffError
from gentest.validate.roundtrip import roundtripper, exec_and_run_callback

# @NOTE: For reasons I don't understand, stack line numbers change between runs when we directly raise here instead of return the errors
#        which triggers the flaky test detection, so this weird pattern of returning them is necessary.
def task_roundtrip(expected: mm.Task, conjecture: ConjectureData) -> RoundtripError|None:
    __tracebackhide__ = True

    normalize_expected_task(expected)

    doc = DocumentEmitter()
    try:
        doc.rule(expected)
        code = doc.stringify().strip()
    except Exception as err:
        # @NOTE: unfortunately including these tracebacks incorrectly triggers Hypothesis's flaky test detection, because
        # it seems to expect the exact same error to be returned from the same position every shrink.
        # This doesn't make any sense to me, but I don't have more time to investigate it right now.
        # tb = sys.exc_info()[2]
        return EmitError(expected, conjecture.buffer, err, fmt_task) # .with_traceback(tb)

    try:
        actual = exec_and_run_callback(code, retrieve_task)
    except Exception as err:
        # tb = sys.exc_info()[2]
        return ExecError(expected, conjecture.buffer, code, err, fmt_task) # .with_traceback(tb)

    map_task_ids(expected, actual)
    expected_str = fmt_task(expected)
    actual_str = fmt_task(actual)
    if expected_str != actual_str:
        return DiffError(expected, conjecture.buffer, code, actual, diff_to_str(expected_str, actual_str))


def retrieve_task(exec: Executor) -> mm.Task:
    for block in exec.blocks:
        if isinstance(block, Query):
            continue
        if block.name == "pyrelstd":
            continue
        return block.task

    raise Exception("Could not find rule")


ctx = fixture(fixtures.person_place_thing).finish()
root = GenScope(ctx)

@roundtripper
# @seed(3) # reproduces flaky test results
# @reproduce_failure("6.92.0", b'AXicY2RiYGBkYGRkQAAAAHIABw==') # Repros two vars ground by same ent, prop
@settings(max_examples=50, database=HYPO_DB, )
@given(gen_task(root), gen.data())
def test_task_roundtrip(task: mm.Task, data: gen.DataObject):
    err = task_roundtrip(task, data.conjecture_data)
    if err:
        raise err

