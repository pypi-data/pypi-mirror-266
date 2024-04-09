from relationalai import metamodel as mm
from gentest.gen import ir
from gentest.gen.action import gen_task_body

from gentest.gen.scope import GenScope

def mk_call(op: mm.Task, args: list[mm.Var]):
    return mm.Action(mm.ActionType.Call, mm.Var(mm.Builtins.Task, value=op), [], {prop: arg for prop, arg in zip(op.properties, args)})


def hydrate_call(scope: GenScope, call: ir.Call, into: list[mm.Action]) -> mm.Var|None:
    args = [hydrate_expr(scope, arg, into) for arg in call.args]
    into.append(mk_call(call.op, args))
    if not call.op.properties[-1].is_input:
        return args[-1]

def hydrate_expr(scope: GenScope, expr: ir.Expr|list[ir.Expr], into: list[mm.Action]) -> mm.Var:
    match expr:
        case mm.Var():
            return expr
        case ir.Constant():
            return mm.Var(expr.type, value=expr.value)
        case ir.Call():
            ret = hydrate_call(scope, expr, into)
            assert ret
            return ret
        case list():
            # @FIXME: Correct typing for list vars?
            return mm.Var(mm.Builtins.Any, value=[hydrate_expr(scope, v, into) for v in expr])
        case _:
            raise Exception(f"Unhandled expression type {expr.__class__.__name__}")

def as_mm_action_type(op: ir.AssertOp) -> mm.ActionType:
    match op:
        case ir.AssertOp.Bind:
            return mm.ActionType.Bind
        case ir.AssertOp.Persist:
            return mm.ActionType.Persist
        case ir.AssertOp.Unpersist:
            return mm.ActionType.Unpersist
        case _:
            raise Exception(f"Unhandled action type {op}")

def hydrate_action(scope: GenScope, action: ir.Action, into: list[mm.Action]):
    match action:
        case ir.EntityProvider():
            into.append(mm.Action(mm.ActionType.Get, action.entity, [action.entity.type], action.properties))
        case ir.ComputedProvider():
            hydrate_call(scope, action.call, into)
        case ir.AssertType():
            into.append(mm.Action(as_mm_action_type(action.op), action.entity, [action.type]))
        case ir.AssertProperty():
            into.append(mm.Action(as_mm_action_type(action.op), action.entity, [], {action.property: hydrate_expr(scope, action.value, into)}))
        case ir.Call():
            hydrate_call(scope, action, into)
        case _:
            raise Exception(f"Unhandled action type {action.__class__.__name__}.")

def hydrate_actions(scope: GenScope, actions: list[ir.Action]):
    hydrated_actions = []
    for action in actions:
        hydrate_action(scope, action, hydrated_actions)

    return hydrated_actions, scope

def hydrate(pair: tuple[list[ir.Action], GenScope]):
    hydrated_actions, _ = hydrate_actions(pair[1], pair[0])
    return mm.Task(behavior=mm.Behavior.Query, items=hydrated_actions)

def gen_task(root_scope: GenScope):
    return gen_task_body(root_scope, 5).map(hydrate)

