from typing import List, Set
from contextlib import contextmanager
import pprint
import keyword
import re
import unicodedata
from relationalai import metamodel as mm
from relationalai.clients.test import Document, Install, Query
from gentest.gen import ir

pp = pprint.PrettyPrinter(indent=2, depth=2)

def sanitize_variable_name(input_string):
    input_string = unicodedata.normalize('NFKD', input_string)
    # Replace non-alphanumeric characters with underscores
    sanitized = re.sub(r'\W|^(?=\d)', '_', input_string)

    # Check if the resulting string is a keyword and append an underscore if it is
    if keyword.iskeyword(sanitized):
        sanitized += '_'

    return sanitized


class Scope:
    def __init__(self, parent: 'Scope|None' = None):
        self.mappings: dict[mm.Type|mm.Var, str] = {}
        self.parent = parent
        self.unused_properties: dict[mm.Var, bool] = {}
        self.introduced: set[mm.Var] = set()
        self.used_entity_names: set[str] = set()

    def child(self) -> 'Scope':
        return Scope(self)

    def get(self, of: mm.Type|mm.Var) -> str|None:
        existing = self.mappings.get(of)
        if existing:
            return existing
        if self.parent:
            return self.parent.get(of)

    def constant(self, value: mm.Value) -> str:
        if isinstance(value, list):
            str_repr = f"[{', '.join(self.value(item) for item in value)}]"
        else:
            str_repr = repr(value)
            if str_repr == "nan" or str_repr == "inf" or str_repr == "-inf":
                if isinstance(value, float):
                    str_repr = f"float(\"{str_repr}\")"

        return str_repr

    # @FIXME: When do I ever _not_ want the name unique-ifying of as_root?
    def var(self, of: mm.Type|mm.Var, as_root = True, uses = True) -> str:
        if of in self.unused_properties and uses:
            del self.unused_properties[of]
        existing = self.get(of)
        if existing:
            return existing

        match of:
            case mm.Type():
                str_repr = sanitize_variable_name(of.name)
            case mm.Var():
                if of.value is not None:
                    str_repr = self.constant(of.value)
                elif as_root:
                    base = of.type.name.lower()
                    ix = 1
                    cur = base
                    while cur in self.used_entity_names:
                        ix += 1
                        cur = f"{base}{ix}"

                    self.used_entity_names.add(cur)
                    str_repr = sanitize_variable_name(cur)
                else:
                    str_repr = sanitize_variable_name(f"{of.type.name.lower()}_{str(of)}" )
            case _:
                assert of is None

        self.mappings[of] = str_repr
        return str_repr

    def value(self, of:mm.Var|mm.Value, as_entity = False):
        match of:
            case mm.Var():
                return self.var(of, as_entity)
            case _:
                return self.constant(of)

    def map_property(self, subject: mm.Var, property: mm.Property, var: mm.Var):
        assert not self.mappings.get(var)
        mapped = f"{self.var(subject)}.{sanitize_variable_name(property.name)}"
        self.mappings[var] = mapped

class Builder:
    def __init__(self, document: 'DocumentEmitter', scope: Scope, joiner = "\n"):
        self.doc = document
        self.scope = scope
        self.chunks: List[str] = []
        self.joiner = joiner

    def chunk(self, text: str):
        self.chunks.append(text)

    def stringify(self, joiner: str|None = None):
        joiner = (joiner if joiner else self.joiner)
        return joiner.join(self.chunks)

    @contextmanager
    def nest(self):
        nested = Builder(self.doc, self.scope.child(), f"{self.joiner}    ")
        try:
            yield nested
        finally:
            self.chunk(f"    {nested.stringify()}")

    @contextmanager
    def call(self, op: str, store_to: str|None = None):
        nested = Builder(self.doc, self.scope, joiner = ", ")
        try:
            yield nested
        finally:
            expr = f"{op}({nested.stringify()})"
            if store_to:
                self.chunk(f"{store_to} = {expr}")
            else:
                self.chunk(expr)



class DocumentEmitter:
    @classmethod
    def from_document(cls, doc: Document):
        new = cls()
        for block in doc.blocks:
            match block:
                case Install():
                    new.rule(block.task)
                case Query():
                    new.query(block.task)
                case _:
                    raise Exception(f"Unhandled block type {block}")

        return new

    def __init__(self, graph_ctor: str = "rai.clients.test.Graph(\"test\")", is_nested = False):
        self.graph_name = "graph"
        self.graph_ctor = graph_ctor

        self.scope = Scope()
        self.blocks: List[Builder] = []
        self.uses_types: Set[mm.Type] = set()

        self.is_nested = is_nested
        self.sep = "\n    " if is_nested else "\n"

    def rule(self, task: mm.Task):
        builder = Builder(self, self.scope, self.sep)
        builder.chunk(f"with {self.graph_name}.rule():")
        emit_task(task, builder)
        if len(builder.chunks) > 1:
            self.blocks.append(builder)
            return builder

    def query(self, task: mm.Task):
        builder = Builder(self, self.scope, self.sep)
        builder.chunk(f"with {self.graph_name}.query() as select:")
        emit_task(task, builder)
        if len(builder.chunks) > 1:
            self.blocks.append(builder)
            return builder

    def use(self, type: mm.Type):
        self.uses_types.add(type)

    def stringify(self):

        body = self.sep + self.sep.join([
            "# Types",
            *[f"{self.scope.var(type)} = {self.graph_name}.Type(\"{type.name}\")" for type in self.uses_types],
            "",

            "# Rules",
            *[f"{block.stringify()}\n" for block in self.blocks]
        ])

        return "\n".join([
            "import relationalai as rai",
            "",

            "# Init",
            f"{self.graph_name} = {self.graph_ctor}" if not self.is_nested else f"with {self.graph_ctor} as {self.graph_name}:",
            body,
        ])




def emit_task(task: mm.Task, into: Builder):
    with into.nest() as body:
        for item in task.items:
            emit_action(item, body)

        for v in body.scope.unused_properties:
            body.chunk(body.scope.var(v, uses=False))

def emit_action(action: mm.Action, into: Builder):
    match action.action:
        case mm.ActionType.Bind | mm.ActionType.Persist | mm.ActionType.Unpersist | mm.ActionType.Construct:
            if action.entity.value == mm.Builtins.Return:
                emit_return_action(action, into)
            else:
                emit_assert_action(action, into)
        case mm.ActionType.Get:
            emit_get_action(action, into)
        case mm.ActionType.Call:
            emit_call_action(action, into)

        case _:
            raise Exception(f"Unhandled action type in emitter '{action.action}'.")

def emit_return_action(action: mm.Action, into: Builder):
    # @FIXME: Need to know the actual name of the select here and choose what to name the return var
    with into.call("select", "response") as call:
        for type in action.types:
            call.doc.use(type)
            call.chunk(call.scope.var(type))
        for var in action.bindings.values():
            call.chunk(call.scope.var(var))

def emit_assert_action(action: mm.Action, into: Builder):
    # @FIXME: Check if var is A) subject of a make_identity call, and B) not already provided by another assert/get
    #         to switch to op = "add"
    creates_entity = action.entity not in into.scope.introduced

    match action.action:
        case mm.ActionType.Bind:
            op = "add" if creates_entity else "set"
        case mm.ActionType.Persist:
            op = "persist"
        case  mm.ActionType.Unpersist:
            op = "unpersist"
        case _:
            raise Exception(f"Invalid assert action: {action.action}")

    types = action.types

    if creates_entity:
        subject_type = types[0]
        assert subject_type

        into.doc.use(subject_type)
        op = f"{into.scope.var(subject_type)}.{op}"
        types = types[1:]
    else:
        op = f"{into.scope.var(action.entity, True)}.{op}"

    with into.call(op, into.scope.var(action.entity, True) if creates_entity and not action.entity.value else None) as call:
        for type in types:
            call.doc.use(type)
            call.chunk(call.scope.var(type))

        for (prop, var) in action.bindings.items():
            call.chunk(f"{sanitize_variable_name(prop.name)}={call.scope.var(var)}")


def emit_get_action(action: mm.Action, into: Builder):
    creates_entity = action.entity not in into.scope.introduced

    subject_type = action.types[0]
    assert subject_type

    into.doc.use(subject_type)

    store_to = None
    if creates_entity:
        into.scope.introduced.add(action.entity)
        store_to = into.scope.var(action.entity, True)

    with into.call(into.scope.var(subject_type), store_to) as call:
        if not creates_entity:
            call.chunk(call.scope.var(action.entity, True))

        for type in action.types[1:]:
            into.doc.use(type)
            call.chunk(call.scope.var(type))

        for (prop, var) in action.bindings.items():
            call.scope.map_property(action.entity, prop, var)
            call.scope.unused_properties[var] = True


OP_NAME_MAP = {
    "=": "==",
    "average": "avg",

}

def emit_call_action(action: mm.Action, into: Builder):
    task = action.entity.value
    assert isinstance(task, mm.Task)

    is_infix = ir.implements(task, mm.Builtins.Infix)  # task.name in rel.rel_infix

    if is_infix:
        op = OP_NAME_MAP.get(task.name, task.name)
        p1 = task.properties[0]
        p2 = task.properties[1]
        expr = f"{into.scope.var(action.bindings[p1])} {op} {into.scope.var(action.bindings[p2])}"
        if len(task.properties) > 2:
            res_prop = task.properties[2]
            res = action.bindings[res_prop]
            expr = f"{into.scope.var(res)} = {expr}"

        into.chunk(expr)
    elif task.name == "make_identity":
        pass # this is implicitly handled by the scope.introduced set right now.
        # print(f"@TODO: Handle make_identity in call {str(action)}")
    elif ir.implements(task, mm.Builtins.Aggregate):
        op = OP_NAME_MAP.get(task.name, task.name)
        op = f"{into.doc.graph_name}.aggregates.{op}"
        last_prop = task.properties[-1]
        store_to = action.bindings.get(last_prop, None) if not last_prop.is_input else None # @FIXME: More robust result management
        with into.call(op, into.scope.var(store_to, as_root=True) if store_to else None) as call:
            # @FIXME: agg property names don't match the compiler expected kwargs
            # This all goes  away if group is renamed to per and projection to args (or vice versa in the public agg fns)
            projection = next(prop for prop in task.properties if prop.name == "projection")
            proj_arg = action.bindings.get(projection, None)
            if proj_arg and proj_arg.value and isinstance(proj_arg.value, list):
                for v in proj_arg.value:
                    call.chunk(call.scope.value(v))

            group = next(prop for prop in task.properties if prop.name == "group")
            group_arg = action.bindings.get(group, None)
            if group_arg and group_arg.value:
                call.chunk(f"per={call.scope.var(group_arg)}")
    else:
        op = OP_NAME_MAP.get(task.name, task.name)
        last_prop = task.properties[-1]
        store_to = action.bindings.get(last_prop, None) if not last_prop.is_input else None # @FIXME: More robust result management
        with into.call(op, into.scope.var(store_to) if store_to else None) as call:
            for prop in task.properties:
                if prop == last_prop and store_to:
                    continue
                arg = call.scope.var(action.bindings[prop])
                call.chunk(f"{prop.name}={arg}")
