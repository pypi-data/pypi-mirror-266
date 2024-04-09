from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Sequence

from relationalai.metamodel import Behavior, Var
from relationalai import metamodel as mm

def implements(subtype: mm.Type, supertype: mm.Type, seen: set[mm.Type]|None = None) -> bool:
    if subtype == supertype:
        return True

    if not seen:
        seen = set()
    elif subtype in seen:
        return False

    seen.add(subtype)
    for parent in subtype.parents:
        if implements(parent, supertype, seen):
            return True

    return False

id = 0
def next_id():
    global id
    id += 1
    return id

PRIMITIVE_TYPES = [t for t in vars(mm.Builtins).values() if isinstance(t, mm.Type) and implements(t, mm.Builtins.Primitive)]

@dataclass
class Constant:
    type: mm.Type
    value: Any

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return repr(self.value)

Value = Constant | Var


class Provider(ABC):
    def __init__(self, provides: Sequence[mm.Var]):
        self.provides = provides

    def __str__(self):
        default_name = "var"
        return f"Provide({', '.join(f'{v.name or default_name}_{v.id}' for v in self.provides)})"

class EntityProvider(Provider):
    def __init__(self, entity: mm.Var, properties: Sequence[mm.Property]):
        self.entity = entity
        self.properties = {prop: mm.Var(prop.type, f"{entity.name}{entity.id}.{prop.name}") for prop in properties}
        super().__init__([self.entity, *self.properties.values()])

class ComputedProvider(Provider):
    def __init__(self, call: 'Call'):
        self.call = call
        results = [arg for prop, arg in zip(call.op.properties, call.args) if not prop.is_input and isinstance(arg, mm.Var)]
        super().__init__(results)

def fmt_arg(arg: Any):
    match arg:
        case list():
            return f"[{', '.join(fmt_arg(v) for v in arg)}]"
        case mm.Var():
            return f"{arg.name or 'var'}_{arg.id}"
        case _:
            return str(arg)

@dataclass
class Call(Provider):
    id: int = field(default_factory=next_id, init=False)
    op: mm.Task
    args: 'Sequence[Expr]'

    def __post_init__(self):
        self.provides = [arg for arg, prop in zip(self.args, self.op.properties) if not prop.is_input and isinstance(arg, mm.Var)]

    def __str__(self):
        return f"{self.op.name}({', '.join([f'{str(param)}={fmt_arg(arg)}' for (arg, param) in zip(self.args, self.op.properties)])})"

    def __hash__(self):
        return self.id

    def result(self, type: mm.Type) -> mm.Var:
        for var in self.provides:
            if implements(var.type, type):
                return var

        raise Exception(f"Call provides no result of type {type} in {self}.")


Expr = Value | Call

class AssertOp(Enum):
    Bind = "bind"
    Persist = "persist"
    Unpersist = "unpersist"
    # Construct= "construct"

    def __str__(self):
        return self.name

@dataclass
class AssertProperty:
    id: int = field(default_factory=next_id, init=False)
    op: AssertOp
    entity: Var
    property: mm.Property
    value: Expr

    def __str__(self):
        return f"{str(self.entity)}.{self.op}({str(self.property)} = {str(self.value)})"

    def __hash__(self) -> int:
        return self.id

@dataclass
class AssertType:
    id: int = field(default_factory=next_id, init=False)
    op: AssertOp
    entity: Var
    type: mm.Type
    generated: bool = False

    def __str__(self):
        if self.generated:
            return f"{str(self.entity)} = {self.type.name}.{self.op}()"
        else:
            return f"{str(self.entity)}.{self.op}({self.type.name})"

    def __hash__(self) -> int:
        return self.id


Assert = AssertType | AssertProperty

class Quantifier(Enum):
    pass
    # @FIXME: Others not implemented yet
    # Not = "not"


@dataclass
class Subquery:
    quantifier: Quantifier | None
    task: 'Task'

    def __str__(self):
        lines = [f"{str(self.quantifier)} {str(self.task.behavior)}" ]

        body_lines = []
        body_lines.extend([f"  {str(item)}" for item in self.task.items])
        body = "\n".join(body_lines)

        lines.extend([f"  {line}" for line in body.splitlines()])
        return "\n".join(lines)

Action = Provider | Call | Assert | Subquery

@dataclass
class Task:
    id: int = field(default_factory=next_id, init=False)
    behavior: Behavior
    items: list[Action]

    def __str__(self):
        lines = [str(self.behavior)]
        lines.extend([f"  {str(item)}" for item in self.items])
        return "\n".join(lines)

    def __hash__(self) -> int:
        return self.id
