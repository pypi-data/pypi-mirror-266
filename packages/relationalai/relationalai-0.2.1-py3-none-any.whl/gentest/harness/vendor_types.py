


from typing import Protocol
from hypothesis.core import HypothesisHandle

class HypothesisTestFn(Protocol):
    is_hypothesis_test: bool
    hypothesis: HypothesisHandle

    def __call__(self, *args, **kwargs):
        pass
