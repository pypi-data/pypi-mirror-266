from hypothesis import settings, given, strategies as gen
from hypothesis.internal.conjecture.data import ConjectureData
from gentest.gen.document import gen_document
from relationalai.clients.test import Document

from gentest import fixtures
from gentest.gen.context import fixture
from gentest.gen.scope import GenScope
from gentest.validate.diff import diff_to_str

from gentest.emit import DocumentEmitter
from gentest.validate.mapping import map_document_ids, normalize_expected_task
from gentest.util import fmt_task
from gentest.harness.database import HYPO_DB
from gentest.validate.errors import RoundtripError, EmitError, ExecError, DiffError
from gentest.validate.roundtrip import roundtripper, exec_and_run_callback

# @NOTE: For reasons I don't understand, stack line numbers change between runs when we directly raise here instead of return the errors
#        which triggers the flaky test detection, so this weird pattern of returning them is necessary.
def document_roundtrip(expected: Document, conjecture: ConjectureData) -> RoundtripError|None:
    __tracebackhide__ = True

    for block in expected.blocks:
        normalize_expected_task(block.task)

    try:
        doc = DocumentEmitter.from_document(expected)
        code = doc.stringify().strip()
    except Exception as err:
        # @NOTE: unfortunately including these tracebacks incorrectly triggers Hypothesis's flaky test detection, because
        # it seems to expect the exact same error to be returned from the same position every shrink.
        # This doesn't make any sense to me, but I don't have more time to investigate it right now.
        # tb = sys.exc_info()[2]
        return EmitError(expected, conjecture.buffer, err) # .with_traceback(tb)

    try:
        actual: Document = exec_and_run_callback(code)
    except Exception as err:
        # tb = sys.exc_info()[2]
        return ExecError(expected, conjecture.buffer, code, err) # .with_traceback(tb)

    zipped_blocks = map_document_ids(expected, actual)

    for (expected_block, actual_block) in zipped_blocks:
        expected_str = fmt_task(expected_block.task)
        actual_str = fmt_task(actual_block.task)
        if expected_str != actual_str:
            # @FIXME: we're accidentally erasing all the information about the document itself here.
            #         Even though they're very similar this should probably be a different error type
            #         unless I can think of a good way to handle that attribution?
            return DiffError(expected, conjecture.buffer, code, actual, diff_to_str(expected_str, actual_str))

ctx = fixture(fixtures.person_place_thing).finish()
root = GenScope(ctx)

@roundtripper
# @seed(3) # reproduces flaky test results
# @reproduce_failure("6.92.0", b'AXicY2RiYGBkYGRkQAAAAHIABw==') # Repros two vars ground by same ent, prop
@settings(max_examples=50, database=HYPO_DB, )
@given(gen_document(root), gen.data())
def test_document_roundtrip(document: Document, data: gen.DataObject):
    err = document_roundtrip(document, data.conjecture_data)
    if err:
        raise err
