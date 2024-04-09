from typing import cast
from hypothesis import strategies as gen
from hypothesis.strategies import SearchStrategy as Strategy
from gentest.gen.group_limited import group_limiter
from gentest.gen.scope import GenScope
from gentest.gen.staged import staged
from gentest.gen import ir
from gentest.gen.context import GenContext

#-------------------------------------------------------------------------------
# Provisioning
#-------------------------------------------------------------------------------

def gen_entity_provider(ctx: GenContext) -> Strategy[ir.EntityProvider]:
    return ctx.sample_non_primitive_type().flatmap(
        lambda type: gen.builds(
            ir.EntityProvider,
            entity = gen.builds(ir.Var, type=gen.just(type), name=gen.just(f"{type.name}")),
            properties = gen.lists(gen.sampled_from(type.properties), unique=True) if type.properties else gen.just([])))

def gen_computed_provider(scope: GenScope) -> Strategy[ir.ComputedProvider]:
    # @FIXME: This doesn't work if the scope has no vars in it...
    if not scope.vars:
        return gen.nothing()
    computed_strat = scope.gen_computed(None)
    agg_strat = scope.gen_agg(None)
    return gen.builds(
        ir.ComputedProvider,
        group_limiter(
            gen.one_of(
                computed_strat if computed_strat is not None else  gen.nothing(),
                agg_strat if agg_strat is not None else  gen.nothing()),
            expr=6))

def gen_provider(scope: GenScope) -> Strategy[ir.Provider]:
    return gen.one_of(
        gen_computed_provider(scope),
        gen_entity_provider(scope.context))

def gen_provision_stage(root: GenScope, min_size=0, max_size=5) -> Strategy[tuple[list[ir.Action], GenScope]]:
    def populate_scope(providers: list[ir.Provider]) -> tuple[list[ir.Action], GenScope]:
        sub_builder = root.build()
        for item in providers:
            sub_builder.provide(item)

        return (cast(list[ir.Action], providers), sub_builder.finish())
    return gen.lists(gen_provider(root), min_size=min_size, max_size=max_size).map(populate_scope)

#-------------------------------------------------------------------------------
# Consumption
#-------------------------------------------------------------------------------

def gen_consumer(scope: GenScope):
    return gen.one_of(
        scope.gen_filter(),
        scope.gen_assert())

def gen_consumption_stage(scope: GenScope, *, min_size=0, max_size=15) -> Strategy[tuple[list[ir.Action], GenScope]]:
    return gen.lists(gen_consumer(scope), min_size=min_size, max_size=max_size).map(lambda body: (cast(list[ir.Action], body), scope))

#-------------------------------------------------------------------------------
# Staged Generation
#-------------------------------------------------------------------------------

def gen_stage(actions: list[ir.Action], scope: GenScope):
    return (gen_consumption_stage(scope) | gen_provision_stage(scope)).map(lambda pair: (actions + pair[0], pair[1]))

def gen_task_body(root: GenScope, max_stages: int):
    return gen_provision_stage(root, min_size=1, max_size=5).flatmap(lambda pair: staged(gen_stage, pair, lambda actions, _: len(actions) > 50, max_stages=max_stages))
