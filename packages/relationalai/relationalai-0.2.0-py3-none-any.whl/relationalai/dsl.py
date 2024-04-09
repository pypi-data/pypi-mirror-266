from enum import Enum
import inspect
from itertools import zip_longest
import re
import threading
import typing
from typing import Any, Dict, List, Optional, Set, Tuple, TypeGuard, Union, get_type_hints
import numbers
import os
import sys
import datetime
import hashlib
import traceback
import rich

from pandas import DataFrame

from .metamodel import Behavior, Builtins, ActionType, Var, Task, Action, Builder, Type as mType, Property as mProperty
from . import debugging
from .errors import Errors, RAIException, RelQueryError

from bytecode import Instr, Bytecode

#--------------------------------------------------
# Constants
#--------------------------------------------------

RESERVED_PROPS = ["add", "set", "persist", "unpersist"]

#--------------------------------------------------
# Helpers
#--------------------------------------------------

def to_var(x:Any):
    if isinstance(x, Var):
        return x
    if getattr(x, "_to_var", None):
        return to_var(x._to_var())
    if isinstance(x, ContextSelect):
        return x._vars[0]
    if isinstance(x, mProperty):
        return Var(value=x)
    if isinstance(x, mType):
        return Var(value=x)
    if isinstance(x, Producer):
        x._use_var()
        return x._var
    if isinstance(x, list) or isinstance(x, tuple):
        return Var(Builtins.Any, value=[to_var(i) for i in x])
    if isinstance(x, str):
        return Var(Builtins.String, None, x)
    if isinstance(x, numbers.Number):
        return Var(Builtins.Number, None, x)
    if isinstance(x, datetime.datetime) or isinstance(x, datetime.date):
        return Var(value=x)
    raise Exception(f"Unknown type: {type(x)}\n{x}")

build = Builder(to_var)

def to_list(x:Any):
    if isinstance(x, list):
        return x
    if isinstance(x, tuple):
        return list(x)
    return [x]

def is_static(x:Any):
    if isinstance(x, Var):
        return x.value is not None
    if isinstance(x, Type):
        return True
    if isinstance(x, str):
        return True
    if isinstance(x, Producer):
        return is_static(to_var(x))
    if isinstance(x, numbers.Number):
        return True
    if isinstance(x, list):
        return all(is_static(i) for i in x)
    if isinstance(x, tuple):
        return all(is_static(i) for i in x)
    if isinstance(x, dict):
        return all(is_static(i) for i in x.values())
    return False

def is_collection(x:Any) -> TypeGuard[Union[List, Tuple, Set]]:
    return isinstance(x, list) or isinstance(x, tuple) or isinstance(x, set)

#--------------------------------------------------
# Base
#--------------------------------------------------

id = 0
def next_id():
    global id
    id += 1
    return id

#--------------------------------------------------
# Producer
#--------------------------------------------------

class Producer():
    def __init__(self, graph:'Graph', builtins:List[str]):
        self._id = next_id()
        self._graph = graph
        self._builtins = builtins
        self._subs = {}

    def __getattribute__(self, name: str) -> Any:
        if name.startswith("_") or name in self._builtins:
            return object.__getattribute__(self, name)
        if name == "getdoc":
            rich.print("[red bold]GETDOC CALLED")
            traceback.print_stack()
            return
        self._subs[name] = self._make_sub(name, self._subs.get(name))
        return self._subs[name]

    def _make_sub(self, name:str, existing:Optional['Producer']=None) -> Any:
        raise Exception("Implement Producer._make_sub")

    def _use_var(self):
        pass

    #--------------------------------------------------
    # Boolean overloads
    #--------------------------------------------------

    def __bool__(self):
        # This doesn't seem to be safe as Python can call bool on Producers in lots of random cases
        # Errors.invalid_bool(Errors.call_source(3))
        # class_name = self.__class__.__name__
        # raise TypeError(f"Can't convert an {class_name} to a boolean.")
        return True

    #--------------------------------------------------
    # Math overloads
    #--------------------------------------------------

    def _wrapped_op(self, op, left, right):
        args = [left, right]
        return Expression(self._graph, op, args)

    def __add__(self, other):
        return self._wrapped_op(Builtins.plus, self, other)
    def __radd__(self, other):
        return self._wrapped_op(Builtins.plus, other, self)

    def __mul__(self, other):
        return self._wrapped_op(Builtins.mult, self, other)
    def __rmul__(self, other):
        return self._wrapped_op(Builtins.mult, other, self)

    def __sub__(self, other):
        return self._wrapped_op(Builtins.minus, self, other)
    def __rsub__(self, other):
        return self._wrapped_op(Builtins.minus, other, self)

    def __truediv__(self, other):
        return self._wrapped_op(Builtins.div, self, other)
    def __rtruediv__(self, other):
        return self._wrapped_op(Builtins.div, other, self)

    def __pow__(self, other):
        return self._wrapped_op(Builtins.pow, self, other)
    def __rpow__(self, other):
        return self._wrapped_op(Builtins.pow, other, self)

    def __neg__(self):
        return self._wrapped_op(Builtins.mult, self, -1)

    #--------------------------------------------------
    # Filter overloads
    #--------------------------------------------------

    def __gt__(self, other):
        return self._wrapped_op(Builtins.gt, self, other)
    def __ge__(self, other):
        return self._wrapped_op(Builtins.gte, self, other)
    def __lt__(self, other):
        return self._wrapped_op(Builtins.lt, self, other)
    def __le__(self, other):
        return self._wrapped_op(Builtins.lte, self, other)
    def __eq__(self, other) -> Any:
        return self._wrapped_op(Builtins.eq, self, other)
    def __ne__(self, other) -> Any:
        return self._wrapped_op(Builtins.neq, self, other)

    #--------------------------------------------------
    # Context management
    #--------------------------------------------------

    def __enter__(self):
        self._graph._push(self)

    def __exit__(self, *args):
        self._graph._pop(self)

#--------------------------------------------------
# Context
#--------------------------------------------------

class TaskExecType(Enum):
    Query = 1
    Rule = 2
    Procedure = 3

class ContextSelect(Producer):
    def __init__(self, context:'Context'):
        super().__init__(context.graph, ["add"])
        self._context = context
        self._select_len = None
        self._insts = []
        self._vars = []
        self._props = {}

    def _assign_vars(self):
        task = self._context._task
        if not len(self._vars) and self._select_len:
            self._insts = to_list(Vars(self._select_len))
            self._vars = [to_var(v) for v in self._insts]
            task.properties = [Builtins.Relation.properties[i] for i in range(self._select_len)]
            task.bindings.update({Builtins.Relation.properties[i]: v for i, v in enumerate(self._vars)})

    def __call__(self, *args: Any) -> Any:
        graph = self._context.graph
        task = self._context._task
        if task.behavior == Behavior.Query \
            and self._context._exec_type in [TaskExecType.Query, TaskExecType.Procedure]:
            if isinstance(args[0], tuple):
                args = args[0]
            graph._action(build.return_(list(args)))
        else:
            #TODO: good error message depending on the type of task we're dealing with
            raise Exception("Can't select in a non-query")
        return self._context

    def __getattribute__(self, __name: str) -> Any:
        if __name.startswith("_") or __name in ["add"]:
            return object.__getattribute__(self, __name)
        elif __name in self._props:
            return Instance(self._context.graph, ActionType.Get, [], {}, var=to_var(self._props[__name]))
        else:
            return getattr(Instance(self._context.graph, ActionType.Get, [], {}, var=to_var(self._vars[0])), __name)

    def add(self, item, **kwargs):
        arg_len = len(kwargs) + 1
        if self._select_len is not None and arg_len != self._select_len:
            raise Exception("Add must be provided the same arguments in each branch")
        self._select_len = arg_len
        self._assign_vars()
        if len(self._props) and set(self._props.keys()) != set(kwargs.keys()):
            raise Exception("Add must be provided the same properties in each branch")
        elif len(self._props) == 0:
            for k, v in zip(kwargs.keys(), self._vars[1:]):
                self._props[k] = v

        graph = self._context.graph
        graph._action(build.return_([item, *[kwargs[k] for k in self._props.keys()]]))

class Context():
    def __init__(self, graph:'Graph', *args, behavior=Behavior.Query, op=None,
                 exec_type=TaskExecType.Rule, dynamic=False, name="None",
                 inputs=None, outputs=None, engine=None):
        self._id = next_id()
        self.results = DataFrame()
        self.graph = graph
        self._task = Task(behavior=behavior)
        self._op = op
        self._args = list(args)
        self._exec_type = exec_type
        self._select_len = None
        self._rel = None
        self._dynamic = dynamic
        self._name = name
        self._inputs = inputs
        self._outputs = outputs
        self._engine= engine

    def __enter__(self):
        debugging.set_source(self._task, dynamic=self._dynamic)
        self.graph._push(self)
        return ContextSelect(self)

    def __exit__(self, *args):
        # If no exception info has been passed to args,
        # then proceed with the normal exit process.
        # Otherwise, return False to propagate the exception.
        if args[0] is None:
            try:
                self.graph._pop(self)
            except KeyboardInterrupt as e:
                print("Canceling transactions...")
                self.graph.resources.cancel_pending_transactions()
                raise e
            except RAIException as e:
                raise RAIException(e.message) from None
            except RelQueryError:
                raise RAIException("An error occured translating Python into RelationalAI") from None
        else:
            self.graph._pop(self, exec=False)
        return False

    def _ensure_rel(self, vs:List[Var]):
        if self._rel is None:
            self._rel = build.relation_action(ActionType.Get, self._task, vs)
        self.graph._action(self._rel)

    def __iter__(self):
        if self._exec_type != TaskExecType.Query:
            raise Exception("Can't iterate over a non-query task")
        else:
            return self.results.itertuples(index=False)

    def _repr_html_(self):
        if self._exec_type == TaskExecType.Query:
            return self.results.to_html(index=False)

    def __str__(self):
        if self._exec_type == TaskExecType.Query:
            return self.results.to_string(index=False)
        return super().__str__()

#--------------------------------------------------
# Type
#--------------------------------------------------

def hash_values_sha256_truncated(args):
    combined = ''.join(map(str, args))
    combined_bytes = combined.encode('utf-8')
    hasher = hashlib.sha256()
    hasher.update(combined_bytes)
    hash_128_bit = hasher.digest()[:16]
    return hash_128_bit

class Type(Producer):
    def __init__(self, graph:'Graph', name:str, builtins:List[str] = [], scope:str=""):
        super().__init__(graph, ["add", "persist", "extend", "known_properties"] + builtins)
        self._type = mType(scope+name)
        self._scope = scope
        if graph._config.get("compiler.use_value_types", False):
            self._type.parents.append(Builtins.ValueType)
            install = build.install(self._type)
            self._graph._action(install)
            debugging.set_source(install)

    def __call__(self, *args, **kwargs):
        return Instance(self._graph, ActionType.Get, [self, *args], kwargs, name=self._type.name.lower(), scope=self._scope)

    def add(self, *args, **kwargs):
        inst = Instance(self._graph, ActionType.Bind, [self, *args], kwargs, name=self._type.name.lower(), is_add=True, scope=self._scope)
        if is_static(args) and is_static(kwargs):
            params = [Var(value=t.name) for t in inst._action.types]
            params.extend(inst._action.bindings.values())
            inst._action.entity.value = hash_values_sha256_truncated(params)
        elif all([isinstance(a, Type) for a in args]):
            self._graph._action(build.ident(inst._action))
        inst._add_to_graph()
        return inst

    def persist(self, *args, **kwargs):
        inst = Instance(self._graph, ActionType.Persist, [self, *args], kwargs, name=self._type.name.lower(), is_add=True, scope=self._scope)
        if is_static(args) and is_static(kwargs):
            params = [Var(value=t.name) for t in inst._action.types]
            params.extend(inst._action.bindings.values())
            inst._action.entity.value = hash_values_sha256_truncated(params)
        elif all([isinstance(a, Type) for a in args]):
            self._graph._action(build.ident(inst._action))
        inst._add_to_graph()
        return inst

    def extend(self, *args, **kwargs):
        for arg in args:
            if not isinstance(arg, Type):
                raise Exception("Can only extend a type with another type")
            with self._graph.rule(dynamic=True):
                a = arg()
                a.set(self)
            with self._graph.rule(dynamic=True):
                a = arg()
                neue = self(a)
                for k, v in kwargs.items():
                    if isinstance(v, Property):
                        v = getattr(a, v._prop.name)
                    neue.set(**{k:v})

    def __or__(self, __value: Any) -> 'TypeUnion':
        if isinstance(__value, Type):
            return TypeUnion(self._graph, [self, __value])
        if isinstance(__value, TypeUnion):
            return TypeUnion(self._graph, [self, *__value._types])
        raise Exception("Can't or a type with a non-type")

    def _make_sub(self, name: str, existing=None):
        if existing is not None:
            return existing
        return Property(self._graph, name, [self._type], self, scope=self._scope)

    def known_properties(self):
        return [p.name for p in self._type.properties]

#--------------------------------------------------
# TypeUnion
#--------------------------------------------------

class TypeUnion(Producer):
    def __init__(self, graph:'Graph', types:List[Type]):
        super().__init__(graph, [])
        self._types = types

    def __call__(self, *args, **kwargs) -> 'ContextSelect':
        if not len(self._graph._stack.stack):
            raise Exception("Can't create an instance outside of a context")
        graph = self._graph
        with graph.union(dynamic=True) as union:
            for t in self._types:
                with graph.scope():
                    union.add(t(*args, **kwargs))
        return union

    def __or__(self, __value: Any) -> 'TypeUnion':
        if isinstance(__value, Type):
            return TypeUnion(self._graph, [*self._types, __value])
        if isinstance(__value, TypeUnion):
            return TypeUnion(self._graph, [*self._types, *__value._types])
        raise Exception("Can't or a type with a non-type")

    def _make_sub(self, name: str, existing=None):
        if existing is not None:
            return existing
        return Property(self._graph, name, [t._type for t in self._types], self)

#--------------------------------------------------
# Property
#--------------------------------------------------

class Property(Producer):
    def __init__(self, graph:'Graph', name:str, types:List[mType], provider:Type|TypeUnion, scope:str=""):
        super().__init__(graph, ["to_property", "has_many"])
        self._name = name
        self._type = types[0]
        self._scope = scope
        self._provider = provider
        self._prop = build.property_named(scope+name, types)

    def __call__(self, key:Any, value:Any):
        action = build.relation_action(ActionType.Get, self._prop, [key, value])
        self._graph._action(action)

    def _use_var(self):
        raise Exception("Support properties being used as vars")

    def _make_sub(self, name: str, existing=None):
        raise Exception("Support properties on properties?")

    def to_property(self):
        return self._prop

    def has_many(self):
        self._graph._check_property(self._prop, multi_valued=True)

#--------------------------------------------------
# Instance
#--------------------------------------------------

class Instance(Producer):
    def __init__(self, graph:'Graph', action_type:ActionType, positionals:List[Any], named:Dict[str,Any], var:Var|None=None, name=None, is_add=False, scope:str=""):
        super().__init__(graph, RESERVED_PROPS)
        self._action = Action(action_type, to_var(var) if var else Var(name=name))
        self._actions = [self._action]
        self._sets = {}
        self._context = graph._stack.active()
        self._scope = scope
        available_types = []
        last_pos_var = None

        #--------------------------------------------------
        # Positionals
        #--------------------------------------------------
        for pos in positionals:
            if isinstance(pos, Type):
                self._action.append(pos._type)
            elif isinstance(pos, Instance):
                self._action.append(to_var(pos))
                available_types.extend(pos._action.types)
                if last_pos_var:
                    self._graph._action(build.eq(last_pos_var, self._action.entity))
                last_pos_var = self._action.entity
            elif isinstance(pos, TypeUnion):
                self._action.append(to_var(pos()))
                available_types.extend([t._type for t in pos._types])
                if last_pos_var:
                    self._graph._action(build.eq(last_pos_var, self._action.entity))
                last_pos_var = self._action.entity
            elif isinstance(pos, Producer):
                self._action.append(to_var(pos))
                if last_pos_var:
                    self._graph._action(build.eq(last_pos_var, self._action.entity))
                last_pos_var = self._action.entity
            else:
                raise Exception(f"Unknown input type: {pos}")
        available_types.extend(self._action.types)

        #--------------------------------------------------
        # Handle properties
        #--------------------------------------------------
        for name, val in named.items():
            prop = build.property_named(scope+name, available_types)

            if val is None:
                raise Exception(f"{prop}'s value is None, please provide a value for the property")

            prop_var = to_var(val)
            if is_collection(prop_var.value):
                raise Exception("Can't set a property to a collection")

            if not prop_var.name:
                prop_var.name = prop.name
            if prop_var.value is None:
                self._graph._check_property(prop, unknown_cardinality=True)
            else:
                self._graph._check_property(prop)
            self._action.append(prop, prop_var)

        #--------------------------------------------------
        # Entities
        #--------------------------------------------------
        self._var = self._action.entity
        if self._var.type == Builtins.Unknown and len(self._action.types):
            self._var.type = self._action.types[0]
        if not is_add:
            self._add_to_graph()

    def _add_to_graph(self):
        for action in self._actions:
            self._graph._action(action)

    def __call__(self, *args, **kwargs):
        pass

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            return super().__setattr__(name, value)
        Errors.set_on_instance(Errors.call_source(3), name, value)

    def _make_sub(self, name: str, existing=None):
        if self._sets.get(name) is not None:
            return self._sets[name]
        if existing is not None:
            return InstanceProperty(self._graph, self, name, var=existing._var, scope=self._scope)
        prop = build.property_named(name, self._action.types)
        if self._action.bindings.get(prop):
            return InstanceProperty(self._graph, self, name, var=self._action.bindings[prop], scope=self._scope)
        return InstanceProperty(self._graph, self, name, scope=self._scope)

    def set(self, *args, **kwargs):
        if self._graph._stack.active() is self._context:
            self._sets.update(kwargs)
        Instance(self._graph, ActionType.Bind, [self, *args], kwargs, var=self._var, scope=self._scope)
        return self

    def persist(self, *args, **kwargs):
        Instance(self._graph, ActionType.Persist, [self, *args], kwargs, var=self._var, scope=self._scope)
        return self

    def unpersist(self, *args, **kwargs):
        Instance(self._graph, ActionType.Unpersist, [self, *args], kwargs, var=self._var, scope=self._scope)
        return self

#--------------------------------------------------
# InstanceProperty
#--------------------------------------------------

class InstanceProperty(Producer):
    def __init__(self, graph:'Graph', instance:Instance, name:str, var=None, scope:str=""):
        super().__init__(graph, ["or_", "in_", "add", "extend", "choose"])
        self._instance = instance
        self._prop = build.property_named(scope+name, instance._action.types)
        self._var = var or Var(self._prop.type, name=name)
        self._scope = scope
        new = Instance(self._graph, ActionType.Get, [instance], {name: self._var}, scope=self._scope)
        self._action = new._action

    def __call__(self, *args, **kwargs):
        raise Exception("Properties can't be called")

    def _make_sub(self, name: str, existing=None):
        if existing is not None and existing._instance._context is self._graph._stack.active():
            return existing
        return getattr(Instance(self._graph, ActionType.Get, [self], {}), name)

    def or_(self, other):
        self._graph._remove_action(self._action)
        rel.pyrel_default(self._prop, other, self._instance, self)
        return self

    def in_(self, others):
        other_rel = InlineRelation(self._graph, [(x,) for x in others])
        return self == other_rel

    def _remove_if_unused(self):
        # When calling append/extend we aren't necessarily doing a get on the property,
        # but we will already have added one. If we're the only thing using this get,
        # we remove it so that it doesn't unnecessarily constrain the query.
        remove = True
        for item in reversed(self._graph._stack.items):
            if item is self._action:
                break
            elif isinstance(item, Action):
                if self._var in item.vars():
                    remove = False
                    break
        if remove:
            self._graph._remove_action(self._action)

    def add(self, other):
        self._remove_if_unused()
        self._graph._check_property(self._prop, multi_valued=True)
        rel = Action(ActionType.Bind, to_var(self._instance), [], {self._prop: to_var(other)})
        self._graph._action(rel)

    def extend(self, others):
        self._remove_if_unused()
        self._graph._check_property(self._prop, True)
        for other in others:
            rel = Action(ActionType.Bind, to_var(self._instance), [], {self._prop: to_var(other)})
            self._graph._action(rel)

    def choose(self, num, unique=True):
        self._remove_if_unused()
        items = [getattr(Instance(self._graph, ActionType.Get, [self._instance], {}), self._prop.name) for ix in range(num)]
        if unique:
            for ix in range(num-1):
                items[ix] < items[ix+1]
        return items

#--------------------------------------------------
# Expression
#--------------------------------------------------

class Expression(Producer):
    def __init__(self, graph:'Graph', op:mType|Task, args:List[Any]):

        super().__init__(graph, [])
        self._var = None

        # For calls to tasks with known signatures, normalize their arguments by
        # throwing on missing inputs or constructing vars for missing outputs
        if op.properties and not op.isa(Builtins.Anonymous):
            for prop, arg in zip_longest(op.properties, args):
                if arg is None:
                    if prop.is_input:
                        raise TypeError(f"{op.name} is missing a required argument: '{prop.name}'")
                    else:
                        args.append(Var(prop.type, name=prop.name))

            # Expose the last output as the result, to ensure we don't double-create it in _use_var.
            # @NOTE: Literal values like 1 show up here from calls like `rel.range(0, len(df), 1)`
            if not op.properties[-1].is_input and isinstance(args[-1], Var):
                self._var = args[-1]

        self._expr = build.call(op, args)
        self._graph._action(self._expr)

    def __call__(self, *args, **kwargs):
        raise Exception("Expressions can't be called")

    def _use_var(self):
        if not self._var:
            self._var = Var(Builtins.Unknown)
            prop = build.property_named("result", self._expr.types)
            self._expr.append(prop, self._var)

    def _make_sub(self, name: str, existing=None):
        return None

#--------------------------------------------------
# RelationNS
#--------------------------------------------------

unsafe_symbol_pattern = re.compile(r"[^a-zA-Z0-9_]", re.UNICODE)
def safe_symbol(name: str):
    return f':"{name}"' if unsafe_symbol_pattern.search(name) else f":{name}"

class RelationNS():
    def __init__(self, ns:List[str], name:str, use_rel_namespaces=False):
        if name == "getdoc":
            rich.print("[red bold]GETDOC CALLED")
            traceback.print_stack()
            return
        self._name = name
        self._ns = ns
        self._subs = {}
        self._use_rel_namespaces = use_rel_namespaces
        self._rel = self._build_rel()

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        op = self._rel
        self._ensure_args(len(args))
        return Expression(get_graph(), op, list(args))

    def __getattribute__(self, __name: str) -> Any:
        if __name.startswith("_") or __name in ["add"]:
            return object.__getattribute__(self, __name)
        self._subs[__name] = self._make_sub(__name, self._subs.get(__name))
        return self._subs[__name]

    def _make_sub(self, name: str, existing=None):
        if existing is not None:
            return existing
        ns = self._ns[:]
        if self._name:
            ns.append(self._name)
        return RelationNS(ns, name, use_rel_namespaces=self._use_rel_namespaces)

    def _build_rel(self, arg_count = 0):
        fqn_parts = self._ns + [self._name]
        if self._use_rel_namespaces:
            return build.relation('::'+'::'.join(fqn_parts), arg_count)
        if len(fqn_parts) == 1:
            return build.relation(fqn_parts[0], arg_count)
        else:
            return build.relation(f"{fqn_parts[0]}[{', '.join(safe_symbol(part) for part in fqn_parts[1:])}]", arg_count)

    def _ensure_args(self, arg_count):
        if len(self._rel.properties) <= arg_count:
            self._rel.properties = [Builtins.Relation.properties[i] for i in range(arg_count)]

    def add(self, *args):
        op = self._rel
        self._ensure_args(len(args))
        get_graph()._action(build.relation_action(ActionType.Bind, op, list(args)))

    def _to_var(self):
        return Var(Builtins.Relation, value=self._build_rel())

#--------------------------------------------------
# RawRelation
#--------------------------------------------------

class RawRelation(Producer):
    def __init__(self, graph:'Graph', name:str, arity:int):
        super().__init__(graph, ["add"])
        self._name = name
        self._arity = arity
        self._type = build.relation(self._name, self._arity)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return Expression(self._graph, self._type, list(args))

    def add(self, *args):
        self._graph._action(build.relation_action(ActionType.Bind, self._type, list(args)))

    def _make_sub(self, name: str, existing=None):
        return existing

    def _to_var(self):
        return Var(Builtins.Relation, value=self._type)

#--------------------------------------------------
# InlineRelation
#--------------------------------------------------

class InlineRelation():
    def __init__(self, graph:'Graph', data:List[Tuple]):
        self._var = Var()
        self._graph = graph
        cols = [[] for _ in range(len(data[0]))]
        for row in data:
            for i, val in enumerate(row):
                cols[i].append(to_var(val))

        params = [Var(value=col) for col in cols]
        params.append(self._var)
        q = build.relation_action(ActionType.Get, Builtins.InlineRawData, params)
        self._graph._action(q)

    def _to_var(self):
        return self._var

#--------------------------------------------------
# Symbol
#--------------------------------------------------

class Symbol():
    def __init__(self, name:str):
        self._var = Var(Builtins.Symbol, value=name)

    def _to_var(self):
        return self._var

#--------------------------------------------------
# RelationRef
#--------------------------------------------------

class RelationRef(Producer):
    def __init__(self, graph:'Graph', rel:Task|mType, args:List[Var]):
        super().__init__(graph, [])
        self._rel = rel
        self._args = args
        self._var = args[-1]
        self._action = build.relation_action(ActionType.Get, self._rel, self._args)

    def _use_var(self):
        self._graph._action(self._action)

    def _make_sub(self, name: str, existing=None):
        return getattr(Instance(self._graph, ActionType.Get, [self], {}), name)

    def __enter__(self):
        super().__enter__()
        self._use_var()

#--------------------------------------------------
# Export
#--------------------------------------------------

allowed_export_types = [Type, str, numbers.Number, datetime.datetime, datetime.date, bool]

def check_type(name, type):
    if not any(isinstance(type, t) or (inspect.isclass(type) and issubclass(type, t))
                for t in allowed_export_types):
        raise TypeError(f"Argument '{name}' is an unsupported type: {type}")

def export(model, schema, kwargs):
    def decorator(func):
        # Get type hints of the function
        hints = get_type_hints(func)
        input_types = [hints[name] for name in hints if name != 'return']
        arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        for name in arg_names:
            if name not in hints:
                raise TypeError(f"Argument '{name}' must have a type hint")
            check_type(name, hints[name])

        output_types = []
        ret = hints.get('return')
        if typing.get_origin(ret) == tuple:
            for t in typing.get_args(ret):
                check_type("return", t)
                output_types.append(t)
        else:
            check_type("return", ret)
            output_types.append(ret)

        original_bytecode = Bytecode.from_code(func.__code__)
        new_bytecode = Bytecode()
        new_bytecode.argcount = func.__code__.co_argcount
        new_bytecode.argnames = func.__code__.co_varnames
        new_bytecode.docstring = func.__doc__
        new_bytecode.name = func.__name__

        for instr in original_bytecode:
            if isinstance(instr, Instr) and instr.name == "RETURN_VALUE":
                # Insert a call to the ret function before the return instruction
                if sys.version_info < (3, 11): # 3.10
                    new_bytecode.extend([
                        Instr("STORE_FAST", "______x"),
                        Instr("LOAD_GLOBAL", "ret"),
                        Instr("LOAD_FAST", "______x"),
                        Instr("CALL_FUNCTION", 1),
                    ])
                elif sys.version_info < (3, 12): # 3.11
                    new_bytecode.extend([
                        Instr("STORE_FAST", "______x"),
                        Instr("LOAD_GLOBAL", (True, "ret")),
                        Instr("LOAD_FAST", "______x"),
                        Instr("PRECALL", 0),
                        Instr("CALL", 1),
                    ])
                else: #3.12+
                    new_bytecode.extend([
                        Instr("STORE_FAST", "______x"),
                        Instr("LOAD_GLOBAL", (True, "ret")),
                        Instr("LOAD_FAST", "______x"),
                        Instr("CALL", 1),
                    ])
            else:
                new_bytecode.append(instr)

        # Create a new code object from the modified bytecode
        new_bytecode.append(Instr("RETURN_VALUE"))
        new_code = new_bytecode.to_code()

        # Create a new function from the new code object with the correct globals
        new_func = type(func)(new_code, func.__globals__, func.__name__, func.__defaults__, func.__closure__)

        # Update the globals dictionary of the new function to include 'ret'
        name = f"{schema}.{func.__name__}" if schema else func.__name__
        ctx = Context(model, exec_type=TaskExecType.Procedure, name=name, outputs=output_types, **kwargs)
        with ctx as ret:
            inputs = to_list(Vars(len(arg_names)))
            ctx._inputs = list(zip(arg_names, [to_var(i) for i in inputs], input_types))
            # Get the bytecode of the original function
            new_func.__globals__["ret"] = ret
            # Call the new function with the provided arguments
            new_func(*inputs)

        def wrapper():
            raise Exception("Exports can't be called directly. They are exported to the underlying platform")

        return wrapper
    return decorator

#--------------------------------------------------
# RuleStack
#--------------------------------------------------

class RuleStack():
    def __init__(self, graph:'Graph'):
        self.items = []
        self.stack = []
        self._graph = graph

    def push(self, item):
        self.stack.append(item)
        self.items.append(("push", item))

    def pop(self, item):
        self.stack.pop()
        self.items.append(("pop", item))
        if len(self.stack) == 0:
            compacted = self.compact()
            self.items.clear()
            if len(compacted.items):
                return compacted

    def active(self):
        try:
            cur = self.stack[-1]
            if cur is self._graph._temp_rule:
                Errors.out_of_context(Errors.call_source())
            return cur
        except IndexError:
            Errors.out_of_context(Errors.call_source())

    def _expression_start(self, buffer, single_use_vars):
        consume_from = -1
        if not len(buffer):
            return consume_from
        # we can only pull vars if their only use is for this condition
        used_vars = set(buffer[-1].requires_provides()[0] & single_use_vars)
        # walk buffer in reverse collecting vars in the action until we get one
        # that doesn't provide a var we care about
        for action in reversed(buffer[:-1]):
            if not isinstance(action, Action):
                break
            req, provs, _ = action.requires_provides()
            # don't pull in vars the represent root entities even though they're provided
            # by gets. This prevents scenarios where p = Person() would get pulled in if you
            # did with p.age > 10:
            provs = provs - {action.entity}
            if len(used_vars.intersection(provs)):
                used_vars.update(req & single_use_vars)
                consume_from -= 1
            else:
                break
        return consume_from

    def compact(self) -> Task:
        stack:List[Task] = []
        buffer = []

        var_uses = {}
        for item in self.items:
            if isinstance(item, Action):
                if item.action == ActionType.Get:
                    for var in item.vars():
                        var_uses[var] = var_uses.get(var, 0) + 1
                else:
                    for var in item.vars():
                        var_uses[var] = var_uses.get(var, 0) - 1

        # check for 2 refs - one create and one use
        single_use_vars = set([var for var, uses in var_uses.items() if uses >= 0])

        for item in self.items:
            if not isinstance(item, tuple):
                buffer.append(item)
                continue

            op, value = item
            if op == "push":
                if isinstance(value, Context):
                    if len(buffer):
                        stack[-1].items.extend(buffer)
                        buffer.clear()
                    task = value._task
                elif isinstance(value, RelationRef):
                    if len(buffer):
                        stack[-1].items.extend(buffer)
                        buffer.clear()
                    task = Task()

                elif isinstance(value, Producer):
                    consume_from = self._expression_start(buffer, single_use_vars)
                    stack[-1].items.extend(buffer[:consume_from])
                    buffer = buffer[consume_from:]
                    task = Task()
                else:
                    raise Exception(f"Unknown push type: {type(value)}")

                stack.append(task)

            elif op == "pop":
                cur = stack.pop()
                cur.items.extend(buffer)
                buffer.clear()
                if not len(stack):
                    if not self._graph._config.get("compiler.use_v2", False):
                        cur.normalize()
                    return cur
                if isinstance(value, Context) and value._op:
                    stack[-1].items.append(build.call(value._op, [Var(value=value._args), Var(Builtins.Task, value=cur)]))
                else:
                    stack[-1].items.append(build.call(cur, list(cur.bindings.values())))

        raise Exception("No task found")

#--------------------------------------------------
# Graph
#--------------------------------------------------

locals = threading.local()
locals.graph_stack = []

def get_graph():
    _ensure_stack()
    if not len(locals.graph_stack):
        raise Exception("Outside of a model context")
    return locals.graph_stack[-1]

def _ensure_stack():
    if not hasattr(locals, "graph_stack"):
        locals.graph_stack = []
    return locals.graph_stack

rel = RelationNS([], "")
global_ns = RelationNS([], "", use_rel_namespaces=True)

def alias(ref:Any, name:str):
    var = to_var(ref)
    var.name = name
    return var

def Vars(count) -> Any:
    if count == 1:
        return Instance(get_graph(), ActionType.Get, [], {}, Var(Builtins.Unknown))
    return [Instance(get_graph(), ActionType.Get, [], {}, Var(Builtins.Unknown)) for _ in range(count)]

class Graph:
    def __init__(self, client, name:str):
        self.name = name
        self._stack = RuleStack(self)
        self._temp_rule = Context(self)
        self._executed = []
        self._client = client
        self._config = client.resources.config
        self.resources = client.resources
        self._graph_stack = _ensure_stack()
        self._prop_is_multi = {}

        self._graph_stack.append(self)
        self._stack.push(self._temp_rule)

    #--------------------------------------------------
    # Rule stack
    #--------------------------------------------------

    def _push(self, item):
        self._graph_stack.append(self)
        if self._temp_rule:
            self._pop(self._temp_rule, is_temp=True)
            self._temp_rule = None
        self._stack.push(item)

    def _pop(self, item, exec=True, is_temp=False):
        self._graph_stack.pop()
        task = self._stack.pop(item)
        if exec and task:
            self._exec(item, task)
        if not is_temp and not len(self._stack.stack):
            self._temp_rule = Context(self)
            self._graph_stack.append(self)
            self._stack.push(self._temp_rule)

    def _action(self, action:Action|List[Action]):
        if isinstance(action, list):
            for a in action:
                self._action(a)
            return
        self._stack.items.append(action)

    def _remove_action(self, action):
        self._stack.items.remove(action)

    def _exec(self, context:Context, task):
        if context._exec_type == TaskExecType.Rule:
            self._client.install(f"rule{len(self._executed)}", context._task)
        elif context._exec_type == TaskExecType.Query:
            context.results = self._client.query(context._task)
        elif context._exec_type == TaskExecType.Procedure:
            self._client.export_udf(context._name, context._inputs, context._outputs, context._task, context._engine)
        self._executed.append(context)

    #--------------------------------------------------
    # Property handling
    #--------------------------------------------------

    def _check_property(self, prop:mProperty, multi_valued=False, unknown_cardinality=False):
        name = prop.name
        if name in RESERVED_PROPS:
            Errors.reserved_property(Errors.call_source(), name)

        if not self._config.get("compiler.use_multi_valued", False):
            if multi_valued:
                raise Exception(f"Multi-valued properties aren't enabled. Trying to use a property `{name}` as a multi-valued property")
            return
        elif unknown_cardinality:
            return

        if name in self._prop_is_multi:
            if self._prop_is_multi[name] != multi_valued:
                raise Exception(f"Trying to use a property `{name}` as both singular and multi-valued")
        else:
            self._prop_is_multi[name] = multi_valued
        if not multi_valued and Builtins.FunctionAnnotation not in prop.parents:
            prop.parents.append(Builtins.FunctionAnnotation)


    #--------------------------------------------------
    # Public API
    #--------------------------------------------------

    def Type(self, name:str):
        return Type(self, name)

    def rule(self, **kwargs):
        return Context(self, **kwargs)

    def scope(self, **kwargs):
        return Context(self, **kwargs)

    def query(self, **kwargs):
        return Context(self, exec_type=TaskExecType.Query, **kwargs)

    def export(self, object:str = "", **kwargs):
        return export(self, object, kwargs)

    def found(self, **kwargs):
        return Context(self, op=Builtins.Exists, **kwargs)

    def not_found(self, **kwargs):
        return Context(self, op=Builtins.Not, **kwargs)

    def union(self, **kwargs):
        return Context(self, behavior=Behavior.Union, **kwargs)

    def ordered_choice(self, **kwargs):
        return Context(self, behavior=Behavior.OrderedChoice, **kwargs)

    def read(self, name:str, **kwargs):
        from relationalai.loaders.loader import read_resource_context # We do the late import to break an dependency cycle
        return read_resource_context(self, name, **kwargs)

    def load_raw(self, path:str):
        if os.path.isfile(path):
            if path.endswith('.rel'):
                self._client.load_raw_file(path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith('.rel'):
                        file_path = os.path.join(root, file)
                        self._client.load_raw_file(file_path)

    def exec_raw(self, code:str, readonly=True, raw_results=True, inputs:dict|None = None):
        return self._client.exec_raw(code, readonly=readonly, raw_results=raw_results, inputs=inputs)

    def install_raw(self, code:str, name:str|None=None):
        self._client.install_raw(code, name)

