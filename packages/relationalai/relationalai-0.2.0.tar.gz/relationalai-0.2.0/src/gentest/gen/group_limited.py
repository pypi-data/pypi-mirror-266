from typing import TypeVar
import threading
from hypothesis.strategies._internal.strategies import SearchStrategy
from hypothesis.strategies._internal.recursive import LimitReached

T = TypeVar("T")

class GroupLimitedStrategy(SearchStrategy):
    """A strategy which, when called within a GroupLimiterStrategy, will only run its base strategy if the limit hasn't been reached. When the limit is reached, it'll call the optional exhausted strategy if provided, or throw."""
    _active_group_limits = threading.local()

    @classmethod
    def limit_group(cls, group: str, limit: int|None):
        if limit is None:
            delattr(cls._active_group_limits, group)
        else:
            setattr(cls._active_group_limits, group, limit)

    @classmethod
    def current_limit(cls, group: str):
        return getattr(cls._active_group_limits, group, None)

    @classmethod
    def is_limited(cls, group: str):
        return getattr(cls._active_group_limits, group, None) is not None

    def __init__(self, group: str, strategy: SearchStrategy, exhausted: SearchStrategy|None):
        super().__init__()
        self.group = group
        self.base_strategy = strategy
        self.exhausted = exhausted

    @property
    def remaining(self):
        return getattr(GroupLimitedStrategy._active_group_limits, self.group, None)

    @remaining.setter
    def remaining(self, value):
        return setattr(GroupLimitedStrategy._active_group_limits, self.group, value)

    def do_validate(self):
        self.base_strategy.validate()

    def do_draw(self, data):
        remaining = self.remaining
        if remaining is None:
            raise Exception(f"GroupLimitedStrategy for group {self.group} can only be drawn from within an active group limit. Make sure you've wrapped your draws in a `with group_limit('{self.group}', NUM):`")

        if remaining <= 0:
            if self.exhausted is not None:
                return data.draw(self.exhausted)
            else:
                raise LimitReached
        self.remaining = remaining - 1
        return data.draw(self.base_strategy)

    def __repr__(self):
        return f"GroupLimitedStrategy({self.group}, {self.base_strategy!r})"

class GroupLimiterStrategy(SearchStrategy):
    """A strategy which constrains all descendant GroupLimitedStrategy's of the given groups with the specified limit."""
    def __init__(self, inner: SearchStrategy, limits: dict[str, int]):
        super().__init__()
        self.inner_strategy = inner
        self.limits = limits

    def do_validate(self):
        self.inner_strategy.validate()

    def do_draw(self, data):
        owned_limits = []
        for group, limit in self.limits.items():
            if not GroupLimitedStrategy.is_limited(group):
                owned_limits.append(group)
                GroupLimitedStrategy.limit_group(group, limit)

        try:
            return data.draw(self.inner_strategy)
        finally:
            for group in owned_limits:
                GroupLimitedStrategy.limit_group(group, None)

    def __repr__(self):
        return f"GroupLimiterStrategy({self.limits}, {self.inner_strategy!r})"


def limited_by_group(group: str, strategy: SearchStrategy[T], exhausted: SearchStrategy|None) -> SearchStrategy[T]:
    """Wrap a strategy in a limiter. When `group` has an active limit (set using the `limit_group()` ctx manager), strategy will bail when the limit runs out."""
    return GroupLimitedStrategy(group, strategy, exhausted)

def group_limiter(strategy: SearchStrategy[T], **limits: int) -> SearchStrategy[T]:
    return GroupLimiterStrategy(strategy, limits)














# import threading
# from contextlib import contextmanager

# from hypothesis.errors import InvalidArgument
# from hypothesis.internal.reflection import get_pretty_function_description
# from hypothesis.internal.validation import check_type
# from hypothesis.strategies._internal.strategies import (
#     OneOfStrategy,
#     SearchStrategy,
#     check_strategy,
# )
# from hypothesis.strategies._internal.recursive import LimitReached


# class GroupLimitedStrategy(SearchStrategy):
#     _active_group_limits = threading.local()

#     @classmethod
#     def limit_group(cls, group: str, limit: int|None):
#         if limit == None:
#             delattr(cls._active_group_limits, group)
#         else:
#             setattr(cls._active_group_limits, group, limit)

#     @classmethod
#     def current_limit(cls, group: str):
#         return getattr(cls._active_group_limits, group, None)

#     def __init__(self, group: str, strategy: SearchStrategy, require_limit = False):
#         super().__init__()
#         self.group = group
#         self.base_strategy = strategy
#         self.require_limit = require_limit

#     @property
#     def remaining(self):
#         return getattr(GroupLimitedStrategy._active_group_limits, self.group, None)

#     @remaining.setter
#     def remaining(self, value):
#         return setattr(GroupLimitedStrategy._active_group_limits, self.group, value)

#     def do_validate(self):
#         self.base_strategy.validate()

#     def do_draw(self, data):
#         remaining = self.remaining
#         if remaining == None:
#             assert not self.require_limit
#             return data.draw(self.base_strategy)

#         if remaining <= 0:
#             raise LimitReached
#         self.remaining = remaining - 1
#         return data.draw(self.base_strategy)

#     def __repr__(self):
#         return f"GroupLimitedStrategy({self.group}, {self.base_strategy!r})"

# @contextmanager
# def limit_group(group: str, limit: int):
#     prev = GroupLimitedStrategy.current_limit(group)
#     GroupLimitedStrategy.limit_group(group, limit)
#     try:
#         yield
#     finally:
#         GroupLimitedStrategy.limit_group(group, prev)

# def limited_group(group: str, strategy: SearchStrategy, require_limit = False):
#     """Wrap a strategy in a limiter. When `group` has an active limit (set using the `limit_group()` ctx manager), strategy will bail when the limit runs out."""
