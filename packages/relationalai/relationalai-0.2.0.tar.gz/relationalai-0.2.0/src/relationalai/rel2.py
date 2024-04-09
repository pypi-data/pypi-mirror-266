from collections import defaultdict
from typing import Dict, List, Set, cast

from .metamodel import Behavior, Builtins, Action, ActionType, Property, Type, Var, Task
from . import metamodel as m
from .dsl import build, is_static

gather_vars = m.Utils.gather_vars

#--------------------------------------------------
# Helpers
#--------------------------------------------------

def add(list, item):
    if item not in list:
        list.append(item)

def flatten_vars(vars:List[Var]):
    res = []
    for var in vars:
        if not isinstance(var, Var):
            continue
        if isinstance(var.value, list):
            res.extend(flatten_vars(cast(List[Var], var.value)))
        else:
            res.append(var)
    return res

#--------------------------------------------------
# Frame
#--------------------------------------------------
frame_id = 0

class Frame():
    def __init__(self, task:Task, prev_frame:'Frame|None'=None):
        global frame_id
        self.id = frame_id
        frame_id += 1
        self.flow_graph:Dict[Var, Set[Action]] = defaultdict(set)
        self.roots = set()
        self.static = defaultdict(list)
        self.constraints = defaultdict(set)
        self.get_action:Action|None = None
        self.finalized = False
        self.strict = False
        self.multi_effect = False
        if prev_frame:
            self.merge(prev_frame)
        self.task = task

    def add_action(self, action):
        if not action.entity.isa(Builtins.Intermediate) \
            and not action.types and not action.bindings:
            return

        items = self.task.items
        for item in items:
            if item is action or item.equiv(action):
                return

        items.append(action)

    def stage(self, action:Action):
        for prop, value in action.bindings.items():
            if not prop.is_input or action.entity.isa(Builtins.Filter):
                self.add_dep(value, action)
        # for dep in action.vars(recursive=True):
        #     self.add_dep(dep, action)

    def add_dep(self, var:Var, action:Action):
        for dep_action in self.flow_graph[var]:
            if dep_action.equiv(action):
                return
        self.flow_graph[var].add(action)

    def pull_action(self, action:Action):
        for var in action.vars(recursive=True):
            self.pull_var(var)

        self.add_action(action)

    def pull_var(self, var:Var):
        vars = [var]
        actions = []
        for cur in vars:
            for dep_action in self.flow_graph[cur]:
                if self.is_constrained(cur, dep_action):
                    continue
                vals = [*dep_action.bindings.values()]
                if dep_action.entity.isa(Builtins.Intermediate):
                    if cur not in dep_action.vars():
                        prop = Builtins.Relation.properties[len(dep_action.bindings)]
                        dep_action.bindings[prop] = cur
                if isinstance(dep_action.entity.value, Property) and cur is vals[0]:
                    if vals[1].value is not None:
                        add(actions, dep_action)
                    elif self.has_other_dep(vals[1], dep_action) and not self.is_constrained(vals[1], dep_action):
                        add(actions, dep_action)
                        add(vars, vals[1])
                else:
                    add(actions, dep_action)
                    for sub_var in dep_action.vars(recursive=True):
                        add(vars, sub_var)

        for action in reversed(actions):
            self.add_action(action)
            self.constraints[var].add(action)
        return actions

    def has_other_dep(self, var:Var, action:Action):
        for dep_action in self.flow_graph[var]:
            if var in dep_action.vars() and not dep_action.equiv(action):
                return True
        return False

    def is_constrained(self, var:Var, action:Action):
        for dep_action in self.constraints[var]:
            if dep_action.equiv(action):
                return True
        return False

    #--------------------------------------------------
    # Frame management
    #--------------------------------------------------

    def merge(self, other:'Frame'):
        self.merge_constraints(other)
        # self.roots.update(other.roots)
        for var, actions in other.flow_graph.items():
            self.flow_graph[var].update(actions)

    def merge_constraints(self, other:'Frame'):
        for var, actions in other.constraints.items():
            self.constraints[var].update(actions)

#--------------------------------------------------
# FrameSet
#--------------------------------------------------

class FrameSet():
    def __init__(self):
        self.frames:List[Frame] = []
        self.stack:List[Frame] = []
        self.static = defaultdict(list)
        self.binds = {}
        self.raw = []

    #--------------------------------------------------
    # Walk
    #--------------------------------------------------

    def walk(self, item: m.AllItems, parent=None) -> m.AllItems:
        if isinstance(item, Task):
            self.task(item)
            calls = [build.call(f.task, []) for f in self.frames if f.task.items]
            return Task(behavior=Behavior.Sequence, items=self.raw + calls)
        else:
            raise Exception(f"TODO: Demand for {type(item)}")

    def task(self, task: Task, strict=False):
        return getattr(self, task.behavior.value)(task, strict)

    #--------------------------------------------------
    # Sequence
    #--------------------------------------------------

    def sequence(self, task: Task, strict):
        for item in task.items:
            if item.is_subtask_call():
                self.task(cast(Task, item.entity.value), strict)
            elif item.entity.isa(Builtins.RawCode):
                self.raw.append(item)
            else:
                raise Exception(f"Non call sequence item: {item}")

    #--------------------------------------------------
    # Union
    #--------------------------------------------------

    def union(self, task: Task, strict):
        inputs = self.get_inputs(task)
        for sub in task.items:
            if not sub.is_subtask_call():
                raise Exception(f"Non-scope in a union: {sub}")
            neue_items = []
            for item in cast(Task, sub.entity.value).items:
                if item.entity.isa(Builtins.Return):
                    item = build.relation_action(ActionType.Bind, task, [*inputs] + [*item.bindings.values()])
                neue_items.append(item)

            neue = Task(behavior=Behavior.Query, items=neue_items)
            self.task(neue)

    #--------------------------------------------------
    # Ordered Choice
    #--------------------------------------------------

    def ordered_choice(self, task: Task, strict):
        res = []
        prevs = []
        inputs = self.get_inputs(task)

        for sub in task.items:
            if not sub.is_subtask_call():
                raise Exception(f"Non-scope in an ordered_choice: {sub}")
            neue = Task(behavior=Behavior.Query)
            for item in cast(Task, sub.entity.value).items:
                if item.entity.isa(Builtins.Return):
                    item = build.relation_action(ActionType.Bind, task, [*inputs] + [*item.bindings.values()])
                neue.items.append(item)

            if prevs:
                # add a not around the previous
                for prev in prevs:
                    get = build.relation_action(ActionType.Get, prev, inputs)
                    not_task = Task(behavior=Behavior.Query, items=[get], parents=[Builtins.Inline])
                    neue.items.insert(0, build.call(Builtins.Not, [[], not_task]))

            if not sub == task.items[-1]:
                prev = build.relation("", len(inputs))
                neue.items.append(build.relation_action(ActionType.Bind, prev, inputs))
                prevs.append(prev)

            self.task(neue)
        return res

    #--------------------------------------------------
    # Shred
    #--------------------------------------------------

    def shred(self, sub:Action):
        actions = []
        ident, action = sub.entity, sub.action
        for type in sub.types:
            actions.append(build.relation_action(action, type, [ident]))
        for prop, value in sub.bindings.items():
            actions.append(build.relation_action(action, prop, [ident, value]))
        return actions

    #--------------------------------------------------
    # Query
    #--------------------------------------------------

    def query(self, task:Task, strict):
        orig_items = task.items
        task.items = []
        frame = self.push_frame(task=task, strict=strict)

        # check if this has multiple effects
        effect_count = 0
        for sub in reversed(orig_items):
            if sub.is_subtask_call():
                effect_count += 1
            elif sub.entity.isa(Builtins.Return):
                effect_count += 1
            elif sub.action.is_effect() and sub.entity.isa(Builtins.Relation):
                effect_count += 1
            elif sub.action.is_effect():
                effect_count += len(sub.types) + len(sub.bindings)
            if effect_count > 1:
                break
        frame.multi_effect = effect_count > 1

        for sub in orig_items:
            if sub.action not in [ActionType.Call, ActionType.Construct] and not sub.entity.isa(Builtins.Relation):
                cur = self.frame()
                shredded = self.shred(sub)
                if sub.entity.value is None and shredded:
                    cur.roots.add(sub.entity)
                if sub.action.is_effect():
                    for shred in shredded:
                        self.pull_deps(shred)
                else:
                    for shred in shredded:
                        cur.stage(shred)
            elif sub.is_subtask_call():
                self.split(sub)
                self.task(cast(Task, sub.entity.value))
                if sub.bindings:
                    inputs = self.get_inputs(cast(Task, sub.entity.value))
                    self.frame().stage(build.relation_action(ActionType.Get, sub.entity.value, list(inputs) + [*sub.bindings.values()]))
            elif sub.entity.isa(Builtins.Install):
                self.frame().pull_action(sub)
            elif sub.entity.isa(Builtins.Quantifier):
                neue = self.quantifier(sub)
                self.frame().pull_action(neue)
            elif sub.entity.isa(Builtins.Aggregate):
                self.aggregate(sub)
            elif sub.action.is_effect():
                self.pull_deps(sub)
            else:
                self.frame().stage(sub)

        for ((root, root_action), binds) in self.static.items():
            items = []
            vals = [Var(value=[]) for i in range(len(binds[0].bindings))]
            vars = [Var() for v in vals]

            for bind in binds:
                for ix, var in enumerate(bind.bindings.values()):
                    cast(List[Var], vals[ix].value).append(var)

            # if len(effects):
            #     items.append(build.relation_action(ActionType.Get, root_out, roots))

            items.append(build.relation_action(ActionType.Get, Builtins.RawData, vals + vars))
            items.append(build.relation_action(root_action, root, vars))

            self.push_frame(Task(behavior=Behavior.Query, items=items))
            self.pop_frame()

        popped = self.pop_frame()
        while popped and popped != frame:
            popped = self.pop_frame()


    #--------------------------------------------------
    # Dep Handling
    #--------------------------------------------------

    def pull_deps(self, action:Action):
        did_split = self.split(action)

        if action.action == ActionType.Bind and self.is_static(action):
            self.static[(action.entity.value, action.action)].append(action)
            return

        self.frame().pull_action(action)

        if action.action.is_effect() and did_split:
            self.pop_frame()
        elif action.action.is_effect():
            self.frame().finalized = True

    #--------------------------------------------------
    # Quantifier
    #--------------------------------------------------

    def quantifier(self, action: Action, parent=None):
        group, task = action.bindings.values()
        if task.isa(Builtins.Inline):
            return action
        if group.value:
            raise Exception("Implement grouped quantifiers")

        task = cast(Task, task.value)
        inputs = self.get_inputs(task)

        # build a sub task that represents the body of the not, it binds
        # a relation to the inputs that we can then query for inline
        rel = build.relation("", len(inputs))
        bind = build.relation_action(ActionType.Bind, rel, inputs)
        new = Task(behavior=Behavior.Query, items=[*task.items, bind])
        self.task(new, strict=True)

        # build up an inline query for the actual quantification call
        get = build.relation_action(ActionType.Get, rel, inputs)
        inline_task = Task(behavior=Behavior.Query, items=[get], parents=[Builtins.Inline])
        cur = build.call(action.entity.value, [[], inline_task])

        return cur

    #--------------------------------------------------
    # Aggregate
    #--------------------------------------------------

    def aggregate(self, action: Action):
        # self.frame().finalized = True
        self.split(action)
        # self.pop_frame()

        projection, group, result = action.bindings.values()
        projection = cast(List[Var], projection.value).copy()
        orig_projection = projection.copy()
        group = cast(List[Var], group.value)
        agg = cast(Type, action.entity.value)
        is_extender = agg.isa(Builtins.Extender)

        proj_task = Task(behavior=Behavior.Query, parents=[Builtins.Inline])
        self.push_frame(proj_task)
        for g in group:
            if g in projection:
                new = Var()
                projection[projection.index(g)] = new
                self.frame().pull_action(build.eq(g, new))
            else:
                self.frame().pull_var(g)

        proj_bind = build.relation_action(ActionType.Bind, proj_task, [*projection])
        self.frame().pull_action(proj_bind)
        # for v in projection:
        #     self.constrain(v)
        # for v in group:
        #     self.constrain(v)
        proj_frame = self.pop_frame()
        self.frame().merge_constraints(proj_frame)

        rel = build.relation("", len(group) + 1)
        if is_extender:
            mapped_projection = [Var() for v in projection]
            call = build.relation_action(ActionType.Call, agg, [proj_task, result, *mapped_projection])
            bind = build.relation_action(ActionType.Bind, rel, [*group, result, *mapped_projection])
        else:
            call = build.relation_action(ActionType.Call, agg, [proj_task, result])
            bind = build.relation_action(ActionType.Bind, rel, [*group, result])
        t = Task(behavior=Behavior.Query, items=[call, bind])
        self.push_frame(t)
        self.pop_frame()

        if is_extender:
            get = build.relation_action(ActionType.Get, rel, [*group, result, *orig_projection])
        else:
            get = build.relation_action(ActionType.Get, rel, [*group, result])

        self.frame().stage(get)
        return get

    #--------------------------------------------------
    # Frame management
    #--------------------------------------------------

    def frame(self):
        return self.stack[-1]

    def push_frame(self, task:Task|None = None, strict=False):
        if not task:
            task = Task()
        if self.stack and not strict:
            sub = Frame(task, self.frame())
        else:
            sub = Frame(task)
        sub.strict = strict
        if sub and not sub.task.isa(Builtins.Inline):
            self.frames.append(sub)
        self.stack.append(sub)
        return sub

    def pop_frame(self):
        return self.stack.pop()

    #--------------------------------------------------
    # Root handling
    #--------------------------------------------------

    def root_like_use(self, var:Var, action:Action):
        return var in list(action.bindings.values())[:-1]

    def check_for_root(self, sub:Action, maybe_roots:Set[Var]):
        if not sub.entity.isa(Builtins.Relation) \
           or sub.entity.isa(Builtins.Infix) \
           or sub.entity.isa(Builtins.RawData):
            return
        bindings = flatten_vars(list(sub.bindings.values())[:-1])
        frame = self.frame()
        for var in bindings:
            if var.value is not None:
                continue
            deps = frame.flow_graph[var]
            if not any([self.root_like_use(var, dep) for dep in deps]):
                continue
            maybe_roots.add(var)

    def non_root(self, sub:Action, non_roots:Set[Var]):
        if sub.entity.isa(Builtins.InlineRawData):
            non_roots.update(sub.vars())

    def maybe_roots(self, task:Task, known_roots:Set[Var] = set()):
        maybe_roots = set(known_roots)
        non_roots = set()
        for sub in task.items:
            self.check_for_root(sub, maybe_roots)
            self.non_root(sub, non_roots)
        all_vars = gather_vars(task.items) - non_roots
        if len(all_vars) == 2:
            return all_vars

        return maybe_roots - non_roots

    #--------------------------------------------------
    # Splitting
    #--------------------------------------------------

    def split(self, action:Action):
        if not self.should_split(action):
            return

        frame = self.frame()
        if frame.finalized:
            self.push_frame()
            return True

        for var in frame.roots:
            frame.pull_var(var)

        task = frame.task
        if task.items:
            if frame.get_action is None:
                rel = build.relation(f"t{task.id}", 0)
                rel.parents.append(Builtins.Intermediate)
                frame.get_action = build.relation_action(ActionType.Get, rel, [])
                bind = build.relation_action(ActionType.Bind, rel, [])
                bind.bindings = frame.get_action.bindings
                frame.pull_action(bind)
            maybe_roots = self.maybe_roots(task, frame.roots)
            for root in maybe_roots:
                frame.flow_graph[root].clear()
                frame.flow_graph[root].add(frame.get_action)
            frame.finalized = True
            self.push_frame()
            return True
        return False

    def should_split(self, action:Action):
        frame = self.frame()
        if frame.finalized:
            return True
        if action.action.is_effect() and not frame.strict and frame.multi_effect:
            return True
        if action.is_subtask_call():
            return True
        if action.entity.isa(Builtins.Quantifier) \
            and not [*action.bindings.values()][1].isa(Builtins.Inline):
            return True
        if action.entity.isa(Builtins.Aggregate):
            return True
        return False

    #--------------------------------------------------
    # Helpers
    #--------------------------------------------------

    def is_static(self, action:Action):
        vars = gather_vars([action])
        return all([is_static(v) for v in vars])

    def get_inputs(self, task:Task):
        requires, provides, externals = self.requires_provides(task)
        remaining = (requires | provides) - externals
        inputs = set()
        if self.stack:
            return set(self.frame().flow_graph.keys()) & remaining
        return inputs

    def requires_provides(self, task:Task):
        seen = set()
        sub_requires = set()
        sub_provides = set()
        external = set()
        for i in task.items:
            r, p, _ = i.requires_provides(seen)
            sub_requires.update(r)
            sub_provides.update(p)
        return sub_requires - sub_provides, sub_provides, external

    def reset(self):
        self.frames.clear()
        self.stack.clear()
        self.static.clear()
        self.binds.clear()
        self.raw.clear()