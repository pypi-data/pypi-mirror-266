from abc import ABC
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Concatenate, ParamSpec, TypeVar, cast
from hypothesis.strategies import SearchStrategy as Strategy
from hypothesis import strategies as gen
import rich
from gentest.gen.error import BuilderConsumedError
from gentest.gen.ir import implements

from relationalai import metamodel as mm

def has_outputs(task: mm.Task) -> bool:
    for prop in task.properties:
        if not prop.is_input:
            return True
    return False

K = TypeVar("K")
V = TypeVar("V")
def get_key_for_value(obj: dict[K, V], value: V) -> K:
    for key, val in obj.items():
        if val == value:
            return key
    raise Exception(f"No key found for value {value}")

@dataclass
class GenContextBase(ABC):
    """
    GenContextBase captures the essential data used by a GenContext.
    """
    types: set[mm.Type] = field(default_factory=set)
    tasks: list[mm.Task] = field(default_factory=list)

    def __str__(self):
        console = rich.get_console()
        with console.capture() as capture:
            console.rule("Context")
            console.print("    Types")
            for type in self.types:
                console.print(f"    - {type.name} ({type.id})")
            console.print("    Tasks")
            for task in self.tasks:
                console.print(f"    - {task.name}({', '.join(f'{prop.name}: {prop.type.name}' for prop in task.properties)})")
        return capture.get()



@dataclass
class GenContext(GenContextBase):
    """
    A GenContext stores information about the world that are largely static over the duration of a document.
    """

    _sample_arbitrary_type: Strategy[mm.Type] = field(init = False)
    _sample_non_primitive_type: Strategy[mm.Type] = field(init = False)
    _sample_subtype: dict[mm.Type, Strategy[mm.Type]] = field(init = False, default_factory=dict)

    def __post_init__(self):
        self._sample_arbitrary_type = gen.sampled_from(list(self.types))
        self._sample_non_primitive_type = gen.sampled_from([t for t in self.types if not implements(t, mm.Builtins.Primitive)])

    def sample_type(self, super_type: mm.Type|None = None) -> Strategy[mm.Type]:
        if not super_type:
            return self._sample_arbitrary_type
        else:
            strat = self._sample_subtype.get(super_type)
            if not strat:
                subtypes = [t for t in self.types if implements(t, super_type)]
                if subtypes:
                    strat = gen.sampled_from(subtypes)
                    self._sample_subtype[super_type] = strat
                else:
                    raise Exception(f"No subtypes registered for supertype {super_type}")

            return strat

    def sample_non_primitive_type(self) -> Strategy[mm.Type]:
        return self._sample_non_primitive_type


    def build(self):
        return GenContextBuilder(
            types = self.types.copy(),
            tasks = self.tasks.copy())

# Create a type variable that can be any callable
P = ParamSpec("P")
R = TypeVar("R")

def copy_signature_to_method(original_function: Callable[P, R]):
    def decorator(wrapper_function: Callable) -> Callable[Concatenate[Any, P], R]:
        # Update the wrapper function to have the same signature as the original function
        return cast(Any, wraps(original_function)(wrapper_function))
    return decorator

@dataclass
class GenContextBuilder(GenContextBase):
    """
    Convenience class for constructing a GenContext. Remember that any contexts used for generation _must_ not be mutated.
    """

    finished = False

    def assert_not_finished(self):
        if self.finished:
            raise BuilderConsumedError(self)

    @copy_signature_to_method(mm.Type)
    def type(self, *args, **kwargs):
        type = mm.Type(*args, **kwargs)
        self.register_type(type)
        return type

    @copy_signature_to_method(mm.Task)
    def task(self, *args, **kwargs):
        task = mm.Task(*args, **kwargs)
        self.register_task(task)
        return task

    def register_type(self, type: mm.Type):
        self.assert_not_finished()
        self.types.add(type)

    def register_task(self, task: mm.Task):
        self.assert_not_finished()
        self.tasks.append(task)

    def finish(self) -> GenContext:
        """Efficiently drain the builder's state into a scope. Note that it _cannot_ be reused after this."""
        self.finished = True
        return GenContext(
            types = self.types,
            tasks = self.tasks)

    def snapshot(self) -> GenContext:
        """Construct a scope from the current builder state without consuming the builder."""
        return GenContext(
            types = self.types.copy(),
            tasks = self.tasks.copy())


def base_fixture(builder: GenContextBuilder):
    for k, v in vars(mm.Builtins).items():
        match v:
            case mm.Task():
                if not implements(v, mm.Builtins.Quantifier) and v != mm.Builtins.make_identity:
                    builder.register_task(v)
            case mm.Type():
                if implements(v, mm.Builtins.Primitive):
                    builder.register_type(v)

    return builder

def fixture(cb: Callable[[GenContextBuilder], Any], into: GenContextBuilder|None = None) -> GenContextBuilder:
    if not into:
        into = base_fixture(GenContextBuilder())
    cb(into)
    return into
