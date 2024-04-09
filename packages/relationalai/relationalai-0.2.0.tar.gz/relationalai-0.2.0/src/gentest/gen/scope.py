from abc import ABC
from dataclasses import dataclass, field
from typing import Sequence
from hypothesis import strategies as gen
from hypothesis.strategies import SearchStrategy as Strategy
import rich
from gentest.gen.error import BuilderConsumedError
from gentest.gen.group_limited import group_limiter, limited_by_group
from relationalai import metamodel as mm
from gentest.gen import ir
from gentest.gen.context import GenContext

def gen_python_ident(min_size=1, max_size=10):
    return gen.text(min_size=1, max_size=10, alphabet=gen.characters(
        whitelist_categories=('Lu', 'Ll', 'Lt', 'Lm', 'Lo', 'Nl'),
        whitelist_characters='_'))

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------

SUPPORTS_CONST_GEN = [mm.Builtins.Number, mm.Builtins.Int, mm.Builtins.Decimal, mm.Builtins.String, mm.Builtins.Bool, mm.Builtins.Any]

constant_int_strat = gen.builds(ir.Constant, type=gen.just(mm.Builtins.Int), value=gen.integers())
constant_decimal_strat = gen.builds(ir.Constant, type=gen.just(mm.Builtins.Decimal), value=gen.floats())
constant_number_strat = gen.builds(ir.Constant, type=gen.just(mm.Builtins.Number), value=gen.one_of(gen.integers(), gen.floats()))
constant_string_strat = gen.builds(ir.Constant, type=gen.just(mm.Builtins.String), value=gen.text())
constant_bool_strat = gen.builds(ir.Constant, type=gen.just(mm.Builtins.Bool), value=gen.booleans())
arbitrary_constant_strat = gen.one_of(
    constant_int_strat,
    constant_decimal_strat,
    constant_number_strat,
    constant_string_strat,
    constant_bool_strat)

def gen_constant(type: mm.Type|None):
    match type:
        case None | mm.Builtins.Any:
            return arbitrary_constant_strat
        case mm.Builtins.Int:
            return constant_int_strat
        case mm.Builtins.Decimal:
            return constant_decimal_strat
        case mm.Builtins.Number:
            return constant_number_strat
        case mm.Builtins.String:
            return constant_string_strat
        case mm.Builtins.Bool:
            return constant_bool_strat
        case _:
            raise Exception(f"No generation strategy provided for constants of type {type.name} ({type.id})")



#-------------------------------------------------------------------------------
# Scope
#-------------------------------------------------------------------------------

@dataclass
class GenScopeBase(ABC):
    """
    GenScopeBase captures only the essential data used by a GenScope.
    It's split out to allow the builder and the scope itself to maintain the same interface.
    All non-essential data will be generated when the actual GenScope is constructed by calling builder.finish()
    """
    context: GenContext = field()
    vars: list[mm.Var] = field(default_factory=list)
    entities: list[mm.Var] = field(default_factory=list)
    by_type: dict[mm.Type, list[mm.Var]] = field(default_factory=dict)

    def __str__(self):
        console = rich.get_console()
        with console.capture() as capture:
            console.rule("Scope")
            console.print("    Vars")
            for var in self.vars:
                console.print(f"    - {var.name}: {var.type.name} ({var.id})")

            console.print("    Entities")
            for var in self.entities:
                console.print(f"    - {var.name}: {var.type.name} ({var.id})")
            console.print("    By Type")
            for type, vars in self.by_type.items():
                console.print(f"    - {type.name} ({type.id})")
                for var in vars:
                    console.print(f"        - {var.name}: {var.type.name} ({var.id})")
        return capture.get()


@dataclass
class GenScope(GenScopeBase):
    """
    A GenScope stores information which is largely static over the duration of a task.
    """
    context: GenContext = field()
    vars: list[mm.Var] = field(default_factory=list)
    entities: list[mm.Var] = field(default_factory=list)
    by_type: dict[mm.Type, list[mm.Var]] = field(default_factory=dict)

    task_strategies: dict[mm.Task, Strategy] = field(init=False, default_factory=dict)
    _gen_filter: Strategy[ir.Call] = field(init=False, kw_only=True)
    _gen_computed: dict[mm.Type, Strategy[ir.Call]] = field(init=False, kw_only=True)
    _gen_agg: dict[mm.Type, Strategy[ir.Call]] = field(init=False, kw_only=True)
    _gen_arbitrary_computed: Strategy[ir.Call] = field(init=False, kw_only=True)
    _gen_arbitrary_agg: Strategy[ir.Call] = field(init=False, kw_only=True)

    def __post_init__(self):
        filter_strats: list[Strategy[ir.Call]] = []
        agg_strats: dict[mm.Type, list[Strategy[ir.Call]]] = {}
        computed_strats: dict[mm.Type, list[Strategy[ir.Call]]] = {}


        for task in self.context.tasks:
            is_agg = ir.implements(task, mm.Builtins.Aggregate)
            group = agg_strats if is_agg else computed_strats
            is_infix_filter = ir.implements(task, mm.Builtins.Infix) and task.properties[-1].is_input

            if is_agg:
                strat = self.agg_task_to_strategy(task)
            elif is_infix_filter:
                strat = self.infix_filter_task_to_strategy(task)
            else:
                strat = self.task_to_strategy(task)

            self.task_strategies[task] = strat

            is_filter = True
            for prop in task.properties:
                if not prop.is_input:
                    is_filter = False
                    group.setdefault(prop.type, []).append(strat)

            if is_filter:
                filter_strats.append(strat)

        self._gen_filter = group_limiter(gen.one_of(*filter_strats), expr=4)
        self._gen_agg = {type: gen.one_of(*strats) for type, strats in agg_strats.items() if strats}
        self._gen_computed = {type: gen.one_of(*strats) for type, strats in computed_strats.items() if strats}

        self._gen_arbitrary_agg = gen.one_of(*self._gen_agg.values())
        self._gen_arbitrary_computed = gen.one_of(*self._gen_computed.values())

    def gen_filter(self):
        return self._gen_filter

    def gen_computed(self, type: mm.Type|None):
        return self._gen_arbitrary_computed if type is None or type == mm.Builtins.Any else self._gen_computed.get(type)
        # return gen.deferred(lambda: self._gen_arbitrary_computed if type == None or type == mm.Builtins.Any else self._gen_computed[type])

    def gen_agg(self, type: mm.Type|None):
        return self._gen_arbitrary_agg if type is None or type == mm.Builtins.Any else self._gen_agg.get(type)
        # return gen.deferred(lambda: self._gen_arbitrary_agg if type == None or type == mm.Builtins.Any else self._gen_agg[type])

    def build(self):
        """Construct a builder that copies all the state from the current scope."""
        return GenScopeBuilder(
            context=self.context,
            vars=self.vars[:],
            entities=self.entities[:],
            by_type={k: v[:] for k, v in self.by_type.items()})

    def list_vars(self, type: mm.Type|None):
        """Returns a list of all vars in scope of the given type, or all of them if type is None."""
        return self.vars if type is None or type == mm.Builtins.Any else self.by_type.get(type, [])

    def try_sample_var(self, type: mm.Type|None):
        """Sample a variable of the given type, or any variable in scope if type is None."""
        vars = self.list_vars(type)
        if vars:
            return gen.sampled_from(vars)

    def sample_var(self, type: mm.Type|None):
        """Sample a variable of the given type, or any variable in scope if type is None."""
        vars = self.list_vars(type)
        if not vars:
            raise ValueError(f"Cannot sample vars of type {type}. No variables of given type in scope.")

        return gen.sampled_from(vars)

    def sample_entity(self):
        """Sample an entity variable."""
        vars = self.entities
        if not vars:
            raise ValueError("Cannot sample entity vars. No variables of given type in scope.")

        return gen.sampled_from(vars)

    def get_promotable_vars(self) -> Sequence[mm.Var]:
        """List variables which can be promoted to but are not yet entities."""
        return [v for v in self.vars if v not in self.entities and v.type not in ir.PRIMITIVE_TYPES]

    def sample_promotable_var(self, allow_empty = False):
        """Sample a variable which can be promoted to an entity but is not currently used as one."""
        vars = self.get_promotable_vars()
        if allow_empty and not vars:
            return gen.nothing()

        return gen.sampled_from(self.vars)

    def gen_value(self, type: mm.Type|None):
        strats = []
        if type in SUPPORTS_CONST_GEN or type is None:
            strats.append(gen_constant(type))
        var_strat = self.try_sample_var(type)
        if var_strat is not None:
            strats.append(var_strat)
        return gen.one_of(*strats)

        # can_be_var = self.vars and (type in self.by_type or type == None or type == mm.Builtins.Any)
        # can_be_const = type in SUPPORTS_CONST_GEN or type == None
        # if can_be_var and can_be_const:
        #     return gen.one_of(
        #         gen_constant(type),
        #         self.sample_var(type))
        # elif can_be_var:
        #     return self.sample_var(type)
        # elif can_be_const:
        #     return gen_constant(type)
        # elif type:
        #     # raise Exception(f"No vars provided for requested type {type.name} ({type.id}) which has no constant generator.")
        #     return gen.nothing()
        # else:
        #     raise Exception(f"This should never happen, but apparently the scope has no vars and we're unable to generate any constants.")

    def gen_dyn_expr(self, type: mm.Type|None):
        value_strat = self.sample_var(type)
        agg_strats = self.gen_agg(type)
        computed_strats = self.gen_computed(type)
        if agg_strats is not None and computed_strats is not None:
            return gen.one_of(value_strat, agg_strats, computed_strats)
        elif agg_strats is not None:
            return gen.one_of(value_strat, agg_strats)
        elif computed_strats is not None:
            return gen.one_of(value_strat, computed_strats)
        else:
            return value_strat

    def gen_expr_leaf(self, type: mm.Type|None):
        value_strat = self.gen_value(type)
        agg_strats = self.gen_agg(type)
        computed_strats = self.gen_computed(type)
        if agg_strats is not None and computed_strats is not None:
            return gen.one_of(value_strat, agg_strats, computed_strats)
        elif agg_strats is not None:
            return gen.one_of(value_strat, agg_strats)
        elif computed_strats is not None:
            return gen.one_of(value_strat, computed_strats)
        else:
            return value_strat

    def gen_expr(self, type: mm.Type|None, max_leaves = 6):
        return group_limiter(self.gen_expr_leaf(type), expr=max_leaves)

    def _gen_output(self, property: mm.Property):
        return gen.builds(mm.Var, type=gen.just(property.type))

    def task_to_strategy(self, task: mm.Task) -> Strategy:
        def build_args():
            first = task.properties[0]
            rest = task.properties[1:]
            try:
                return gen.tuples(self.gen_dyn_expr(first.type), *(self.gen_expr(prop.type) if prop.is_input else self._gen_output(prop) for prop in rest))
            except ValueError:
                return gen.nothing()

        def build_exhausted_args():
            first = task.properties[0]
            rest = task.properties[1:]
            try:
                return gen.tuples(self.sample_var(first.type), *(self.gen_value(prop.type) if prop.is_input else self._gen_output(prop) for prop in rest))
            except ValueError:
                return gen.nothing()

        return limited_by_group(
            "expr",
            gen.builds(ir.Call, gen.just(task), gen.deferred(build_args)),
            gen.builds(ir.Call, gen.just(task), gen.deferred(build_exhausted_args)))

    def infix_filter_task_to_strategy(self, task: mm.Task) -> Strategy:
        def build_args():
            return gen.tuples(self.sample_var(None), self.gen_expr(None))

        def build_exhausted_args():
            return gen.tuples(self.sample_var(None), self.gen_value(None))

        return limited_by_group(
            "expr",
            gen.builds(ir.Call, gen.just(task), gen.deferred(build_args)),
            gen.builds(ir.Call, gen.just(task), gen.deferred(build_exhausted_args)))

    def agg_task_to_strategy(self, task: mm.Task) -> Strategy:
        for prop in task.properties:
            if prop.name == "result":
                result_prop = prop
                break
        else:
            raise Exception(f"Could not find result property in aggregate {task.name}({[p.name for p in task.properties]}).")

        def build_args():
            if not self.vars:
                return gen.nothing()

            # @NOTE: It's possible to inline expressions here but that seems like an insane thing to do (?)
            # group = gen.lists(self.gen_expr(None), max_size=6, unique=True)
            # projection = gen.lists(self.gen_expr(None), min_size=1, max_size=6, unique=True)
            projection = gen.lists(self.sample_var(None), min_size=1, max_size=6, unique=True)
            group = gen.lists(self.sample_var(None), max_size=6, unique=True)
            result = self._gen_output(result_prop)
            return gen.tuples(projection, group, result)

        return limited_by_group(
            "expr",
            gen.builds(ir.Call, gen.just(task), gen.deferred(build_args)),
            self.gen_value(result_prop.type)) # @FIXME: This feels nasty but I don't have a better solution atm

    def gen_assert_type(self):
        return gen.builds(
            ir.AssertType,
            op = gen.sampled_from(ir.AssertOp),
            entity = self.sample_entity(),
            type = self.context.sample_non_primitive_type(),
            generated = gen.booleans())

    def gen_new_prop(self, type: mm.Type|None):
        return gen.builds(mm.Property, name=gen_python_ident(), type=gen.just(type) if type else self.context.sample_type())

    def gen_prop_for_entity(self, entity: mm.Var, only_existing = False):
        strategy = gen.sampled_from(entity.type.properties)
        if not only_existing:
            strategy = gen.one_of(strategy, self.gen_new_prop(None))

        return gen.tuples(gen.just(entity), strategy)

    def gen_ent_prop_pair(self, only_existing = False):
        return self.sample_entity().flatmap(lambda entity: self.gen_prop_for_entity(entity, only_existing))

    def gen_assert_property(self):
        return self.gen_ent_prop_pair().flatmap(lambda pair: gen.builds(
            ir.AssertProperty,
            op = gen.sampled_from(ir.AssertOp),
            entity = gen.just(pair[0]),
            property = gen.just(pair[1]),
            value = self.gen_expr(pair[1].type)))

    def gen_assert(self):
        return gen.one_of(self.gen_assert_type(), self.gen_assert_property())

@dataclass
class GenScopeBuilder(GenScopeBase):
    """
    Convenience class for constructing a GenScope. Remember that any scopes used for generation _must_ not be mutated.
    """

    finished = False
    items: list[ir.Provider] = field(default_factory=list)

    def assert_not_finished(self):
        if self.finished:
            raise BuilderConsumedError(self)

    def provide(self, item: ir.Provider):
        """Expose a new set of variables into the scope."""
        self.assert_not_finished()

        self.items.append(item)
        match item:
            case ir.EntityProvider():
                self.entities.append(item.entity)
                self.vars += item.provides
                for v in item.provides:
                    self.by_type.setdefault(v.type, []).append(v)
            case ir.ComputedProvider():
                self.vars += item.provides
                for v in item.provides:
                    self.by_type.setdefault(v.type, []).append(v)
            case _:
                raise Exception(f"GenScopeBuilder does not know how to handle provider of type {type(item)}")

    def finish(self) -> GenScope:
        """Efficiently drain the builder's state into a scope. Note that it _cannot_ be reused after this."""
        self.finished = True
        return GenScope(
            context=self.context,
            vars=self.vars,
            entities=self.entities,
            by_type = self.by_type)

    def snapshot(self) -> GenScope:
        """Construct a scope from the current builder state without consuming the builder."""
        return GenScope(
            context=self.context,
            vars=self.vars[:],
            entities=self.entities[:],
            by_type = {k: v[:] for k, v in self.by_type.items()})
