from typing import TypeVar, Callable, Optional
from hypothesis import strategies as gen
from hypothesis.strategies import SearchStrategy as Strategy

T = TypeVar('T', bound=tuple)
def staged(apply: Callable[..., Strategy[T]], initial: T, until: Optional[Callable[..., bool]] = None, max_stages: int = 5):
    if max_stages <= 0 or until and until(*initial):
        return gen.just(initial)

    return apply(*initial).flatmap(lambda v: staged(apply, v, until=until, max_stages=max_stages - 1))
