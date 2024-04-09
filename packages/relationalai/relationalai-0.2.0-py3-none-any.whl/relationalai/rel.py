from collections import defaultdict
from typing import Any, Dict, Iterable, List, Set, cast

from .rel_emitter import Emitter

from .metamodel import Behavior, Builtins, Action, ActionType, Type, Var, Task
from . import metamodel as m
from . import compiler as c
from .clients import config
from .dsl import build

gather_vars = m.Utils.gather_vars

#--------------------------------------------------
# OrderedSet
#--------------------------------------------------

class OrderedSet:
    def __init__(self):
        self.set:Set[Var] = set()
        self.list:List[Var] = []

    def add(self, item):
        if item not in self.set:
            self.set.add(item)
            self.list.append(item)

    def update(self, items:Iterable[Any]):
        for item in items:
            self.add(item)

    def __contains__(self, item):
        return item in self.set

    def __bool__(self):
        return bool(self.set)

    def __iter__(self):
        return iter(self.list)

#--------------------------------------------------
# Flow
#--------------------------------------------------

class Flow():
    def __init__(self):
        self.tasks:List[Task] = []
        self.inlines:Set[Task] = set()
        self.task_bindings:Dict[Task, OrderedSet] = defaultdict(OrderedSet)
        self.task_deps:Dict[Task, Set[Task]] = defaultdict(set)
        self.provider_stack:List[Dict[Var, Task]] = [{}] # we start with a global scope
        self.task_var_mapping:Dict[Task, Dict[Var, Var]] = defaultdict(dict)

    def push_context(self):
        self.provider_stack.append({})
        neue = Task()
        self.tasks.append(neue)
        return neue

    def pop_context(self, task:Task, inline=False, ignore_deps=False, mappings:Dict[Var, Var]=dict()):
        if not ignore_deps:
            vs = [mappings.get(v, v) for v in gather_vars(task.items)]
            existing = self.fetch(vs, task)
            for e in existing:
                if e != task:
                    self.task_deps[task].add(e)
        if inline:
            self.inlines.add(task)
        self.provider_stack.pop()

    def assoc(self, vars:Iterable[Var], task:Task):
        for var in vars:
            self.provider_stack[-1][var] = task

    def has_var(self, var:Var):
        for provider in reversed(self.provider_stack):
            if var in provider:
                return True
        return False

    def fetch(self, vars:Iterable[Var], cur:Task):
        tasks:Set[Task] = set()
        for var in vars:
            for provider in reversed(self.provider_stack):
                found = provider.get(var)
                if found and found != cur:
                    tasks.add(found)
                    self.task_bindings[found].add(var)
                    break
        return tasks

    def mapped_bindings(self, task:Task, dep:Task, vars:Iterable[Var]|None=None):
        mapped = self.task_var_mapping.get(task)
        bindings = vars or self.task_bindings[dep]
        if mapped and len(mapped):
            return [mapped.get(b, b) for b in bindings]
        return bindings

    def finalize(self):
        final_tasks = []
        for neue in self.tasks:
            for dep in self.task_deps[neue]:
                if dep in self.tasks:
                    neue.items.insert(0, build.relation_action(ActionType.Get, dep, self.mapped_bindings(neue, dep)))
            if self.task_bindings[neue]:
                neue.items.append(build.relation_action(ActionType.Bind, neue, self.task_bindings[neue]))
            if neue not in self.inlines:
                final_tasks.append(neue)
        return final_tasks

    def reset(self):
        self.tasks.clear()
        self.provider_stack.clear()
        self.provider_stack.append({})
        self.task_bindings.clear()

#--------------------------------------------------
# Dataflow
#--------------------------------------------------

class Dataflow(c.Pass):
    def __init__(self, copying=True) -> None:
        super().__init__(copying)
        self.flow = Flow()

    def reset(self):
        super().reset()
        self.flow.reset()

    #--------------------------------------------------
    # Query
    #--------------------------------------------------

    def query(self, task:Task, parent):
        self.query_flow(task)
        if not parent:
            final_tasks = self.flow.finalize()
            task.behavior = Behavior.Sequence
            task.items = [build.relation_action(ActionType.Call, task, []) for task in final_tasks]

    def query_flow(self, task:Task, inline=False, ignore_deps=False):
        flow = self.flow
        neue:Task = flow.push_context()

        for orig in task.items:
            ent:Any = orig.entity
            if orig.action == ActionType.Call and self.local_task(ent):
                flow.assoc(gather_vars(neue.items), neue)
                behavior = ent.value.behavior
                if behavior == Behavior.Union:
                    neue = self.union_call(orig, neue)
                elif behavior == Behavior.OrderedChoice:
                    neue = self.ordered_choice_call(orig, neue)
                elif behavior == Behavior.Query:
                    self.walk(orig, task)
            elif ent.isa(Builtins.Quantifier):
                neue = self.quantifier_call(orig, neue)
            elif ent.isa(Builtins.Aggregate):
                neue = self.aggregate_call(orig, neue)
            else:
                neue.items.append(orig)

        flow.pop_context(neue, inline=inline, ignore_deps=ignore_deps)
        return neue

    def local_task(self, var:Var):
        return isinstance(var.value, Task) and len(var.value.items) > 0

    #--------------------------------------------------
    # Union
    #--------------------------------------------------

    def union_call(self, call:Action, parent:Task):
        has_dep = False
        # run through the subtasks and add them to the flow
        for item in cast(Task, call.entity.value).items:
            neue = self.query_flow(cast(Task, item.entity.value))
            has_dep = has_dep or (parent in self.flow.task_deps[neue])
            rets = [i for i in neue.items if i.entity.value == Builtins.Return]
            if len(rets):
                rets[0].entity.value = call.entity.value
                rets[0].action = ActionType.Bind

        # if one of the subtasks depends on the parent, we need to cut the
        # current task to prevent cycles and carry on in a new one
        if has_dep:
            orig = parent
            self.flow.pop_context(orig)
            self.flow.assoc(gather_vars(orig.items), orig)
            parent = self.flow.push_context()
        parent.items.append(build.relation_action(ActionType.Get, cast(Task, call.entity.value), call.bindings.values()))
        return parent

    #--------------------------------------------------
    # Ordered choice
    #--------------------------------------------------

    def ordered_choice_call(self, call:Action, parent:Task):
        ordered_choice = cast(Task, call.entity.value)
        has_dep = False
        prevs = []
        branches = []

        # depending on whether or not the the subtasks depend on the parent,
        # we'll need to update all the references to the output so that any vars
        # we depend on are included in the result, to guarantee that the choosen
        # values join with the correct original rows
        result_refs = [build.relation_action(ActionType.Get, ordered_choice, call.bindings.values())]
        for item in ordered_choice.items:
            neue:Task = self.query_flow(cast(Task, item.entity.value))
            branches.append(neue)
            # find the return statement, we'll turn it into a bind for the overall orderd_choice
            rets = [i for i in neue.items if i.entity.value == Builtins.Return]
            ret_bindings = []
            if len(rets):
                rets[0].entity.value = neue
                result_refs.append(rets[0])
                ret_bindings = rets[0].bindings.values()
            else:
                rets.append(build.relation_action(ActionType.Bind, neue, ret_bindings))
                neue.items.append(rets[0])
                result_refs.append(rets[0])

            # add a bind for this particular task so that we can negate it in subsequent
            # branches, allowing us to create the ordering
            bind = build.relation_action(ActionType.Bind, ordered_choice, ret_bindings)
            result_refs.append(bind)
            neue.items.append(bind)
            # clear the ret bindings, since this should just return whether or not this
            # branch was successful
            rets[0].bindings.clear()
            # Negate all the previous branches to ensure we only return a value if
            # we're at our position in the order
            for prev in prevs:
                fetch = build.relation_action(ActionType.Get, prev, [])
                result_refs.append(fetch)
                prev_task = Task(items=[fetch])
                neue.items.append(build.call(Builtins.Not, [Var(value=[]), Var(value=prev_task)]))
            prevs.append(neue)

            has_dep = has_dep or (parent in self.flow.task_deps[neue])

        # If one of the branches depends on the parent task, we need to cut the parent
        # and create a new one to prevent cycles
        if has_dep:
            orig = parent
            self.flow.pop_context(orig)
            self.flow.assoc(gather_vars(orig.items), orig)
            # We also need to make sure that branches that don't currently depend on
            # the parent now do, since they also need to join correctly with the original
            # rows
            for branch in branches:
                self.flow.task_deps[branch].add(orig)
            # Update the bindings for the result refs to include the vars we depend on
            for bind in result_refs:
                prop_len = len(bind.bindings)
                for i, var in enumerate(self.flow.task_bindings[orig]):
                    bind.bindings[Builtins.Relation.properties[prop_len+i]] = var
            parent = self.flow.push_context()

        parent.items.append(result_refs[0]) # result_refs[0] is the Get for the ordered_choice
        return parent

    #--------------------------------------------------
    # Quantifiers
    #--------------------------------------------------

    def quantifier_call(self, call:Action, parent:Task):
        quantifier = cast(Task, call.entity.value)
        group, task_var = [*call.bindings.values()]
        sub_task = self.query_flow(cast(Task, task_var.value))

        if isinstance(group.value, list) and len(group.value):
            raise Exception("TODO: grouped quantifiers")

        # Find any vars that this quantified task depends on
        sub_vars = gather_vars(sub_task.items)
        parent_vars = gather_vars(parent.items)
        # Find vars that we explicitly fetch in the child task that are used in the same
        # ent.attr pair in the parent task, so we can remove them as dependencies
        # this allows person.friend.name == "Joe" to not unify with an outer person.friend
        # constraint
        for item in sub_task.items:
            if item.action == ActionType.Get and item.entity in parent_vars:
                sub_vars -= set(item.bindings.values())
        shared = sub_vars & parent_vars
        shared.update([var for var in sub_vars if self.flow.has_var(var)])
        # bind those so we can use them in the quantified task
        sub_task.items.append(build.relation_action(ActionType.Bind, sub_task, shared))

        # create the quantified task, which just gets the subtask
        quantifed_task = Task()
        quantifed_task.items.append(build.relation_action(ActionType.Get, sub_task, shared))

        # add the call to the quantifier
        parent.items.append(build.call(quantifier, [group, Var(value=quantifed_task)]))
        return parent

    #--------------------------------------------------
    # Aggregates
    #--------------------------------------------------

    def aggregate_call(self, call:Action, parent:Task):
        orig = parent
        self.flow.pop_context(orig)
        self.flow.assoc(gather_vars(orig.items), orig)
        agg = cast(Task, call.entity.value)
        (args, group, ret) = [*call.bindings.values()]
        group_vars = cast(List[Var], group.value)

        # create the inner relation we'll aggregate over
        inner = self.flow.push_context()
        inner_vars = cast(List[Var], args.value)
        # to prevent shadowing errors we need to map the inner vars to new vars
        mapped = [Var(name=var.name, type=var.type) for var in inner_vars]
        self.flow.task_var_mapping[inner] = dict(zip(inner_vars, mapped))
        # vars that are in both the projection and grouping needed to be mapped in
        # the projection but made equivalent in the body so the grouping takes effect
        equivs = [(orig, neue) for (orig, neue) in self.flow.task_var_mapping[inner].items() if orig in group_vars]
        for (orig, neue) in equivs:
            inner.items.append(build.relation_action(ActionType.Call, Builtins.eq, [orig, neue]))
        # bind the mapped vars as the output of the inner relation
        inner.items.append(build.relation_action(ActionType.Bind, inner, mapped))
        self.flow.pop_context(inner, inline=True, mappings=dict(zip(mapped, inner_vars)))

        # create the outer aggregate
        outer = self.flow.push_context()
        outer_call = build.relation_action(ActionType.Call, agg, [Var(value=inner), ret])
        outer.items.append(outer_call)
        if agg.isa(Builtins.Extender):
            self.flow.task_bindings[outer].add(ret)
            for g in group_vars:
                self.flow.task_bindings[outer].add(g)
            for ix, var in enumerate(inner_vars):
                self.flow.task_bindings[outer].add(var)
                outer_call.bindings[Builtins.Relation.properties[ix+2]] = var
        else:
            for g in group_vars:
                self.flow.task_bindings[outer].add(g)
            self.flow.task_bindings[outer].add(ret)
        self.flow.pop_context(outer, ignore_deps=True)

        # Resume the flow
        parent = self.flow.push_context()
        parent.items.append(build.relation_action(ActionType.Get, outer, self.flow.task_bindings[outer]))
        return parent


#--------------------------------------------------
# Shredder
#--------------------------------------------------

class Shredder(c.Pass):
    def query(self, task: Task, parent):
        neue_actions = []
        for item in task.items:
            if item.action not in [ActionType.Call, ActionType.Construct] and not item.entity.isa(Builtins.Relation):
                ident, action = item.entity, item.action
                for type in item.types:
                    neue_actions.append(build.relation_action(action, type, [ident]))
                for prop, value in item.bindings.items():
                    neue_actions.append(build.relation_action(action, prop, [ident, value]))
            else:
                neue_actions.append(item)
        task.items = neue_actions

#--------------------------------------------------
# Splinter
#--------------------------------------------------

class Splinter(c.Pass):

    def query(self, task: Task, parent):
        effects = [i for i in task.items if i.action.is_effect()]

        grouped_effects = defaultdict(list)
        for item in effects:
            grouped_effects[(item.action, item.entity.value)].append(item)

        if len(grouped_effects) > 1:
            neue_items = []

            non_effects = [i for i in task.items if not i.action.is_effect()]
            effects_vars = gather_vars(effects)

            fetch = None
            if len(non_effects):
                fetch = self.create_fetch(non_effects, effects_vars)
                neue_items.append(fetch)

            for (k, b) in grouped_effects.items():
                neue_items.append(self.create_effect_query(b, effects_vars, fetch.entity.value if fetch else None))

            task.behavior = Behavior.Sequence
            task.items = neue_items

    #--------------------------------------------------
    # Subtask creation
    #--------------------------------------------------

    def create_fetch(self, non_effects: List[Action], effects_vars: Iterable[Var]):
        fetch = Task()
        non_effects.append(build.relation_action(ActionType.Bind, fetch, effects_vars))
        fetch.items = non_effects
        return build.call(fetch, [])

    def create_effect_query(self, effects: List[Action], effects_vars: Iterable[Var], fetch: Any):
        neue = Task()
        if fetch:
            effects.insert(0, build.relation_action(ActionType.Get, fetch, effects_vars))
        neue.items = effects
        return build.call(neue, [])

#--------------------------------------------------
# SetCollector
#--------------------------------------------------

set_types = [ActionType.Bind, ActionType.Persist, ActionType.Unpersist]

class SetCollector(c.Pass):
    def query(self, query: Task, parent):
        binds = [i for i in query.items if i.action in set_types]
        if len(binds) > 1:
            neue_items = []
            for item in query.items:
                if item.action not in set_types:
                    neue_items.append(item)
            neue_items.extend(self.create_raw(binds))
            query.items = neue_items

    def create_raw(self, binds: List[Action]):
        vals = [Var(value=[]) for i in range(len(binds[0].bindings))]
        vars = [Var() for v in vals]

        for bind in binds:
            for ix, var in enumerate(bind.bindings.values()):
                cast(List[Var], vals[ix].value).append(var)

        return [
            build.relation_action(ActionType.Get, Builtins.RawData, vals + vars),
            build.relation_action(binds[0].action, cast(Type, binds[0].entity.value), vars)
        ]
#--------------------------------------------------
# Compiler
#--------------------------------------------------

class Clone(c.Pass):
    pass

class Compiler(c.Compiler):
    def __init__(self, config:config.Config):
        if config.get("compiler.use_v2", False):
            from . import rel2 as rel2
            super().__init__(Emitter(), [
                Clone(),
                rel2.FrameSet(),
            ])
        else:
            super().__init__(Emitter(), [
                Clone(),
                Dataflow(),
                Shredder(),
                Splinter(),
                SetCollector(),
            ])
