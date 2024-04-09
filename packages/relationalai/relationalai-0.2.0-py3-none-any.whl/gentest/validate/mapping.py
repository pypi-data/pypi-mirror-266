from typing import Iterable, cast
from relationalai import metamodel as mm
from relationalai.clients.test import Document

ASSERT_ACTIONS = [mm.ActionType.Bind, mm.ActionType.Persist, mm.ActionType.Unpersist]
def normalize_expected_task(expected: mm.Task|None):
    if not expected:
        return expected

    normalized = []
    ## @FIXME: Can't just fuse adjacent prior, it's with any prior
    ## @FIXME: Need to pull prev into the new one, not vice versa, since the new one might depend on things the old one didn't
    prev: mm.Action|None = None
    for ix in range(0, len(expected.items)):
        cur = expected.items[ix]
        if cur.action in ASSERT_ACTIONS:
            # Fuse adjacent asserts of the same type to the same entity
            if prev and prev.action == cur.action and prev.entity == cur.entity:
                for type in cur.types:
                    if type not in prev.types:
                        prev.types.append(type)
                for prop in cur.bindings.keys():
                    prev.bindings[prop] = cur.bindings[prop]

                continue

            prev = cur

        normalized.append(cur)

    expected.items = normalized

def normalize_binding_order(action: mm.Action, order: Iterable[mm.Property]):
    bindings = {}
    for key in order:
        bindings[key] = action.bindings.get(key, None)

    action.bindings = bindings
    return action

def map_document_ids(old: Document, new: Document):
    # @FIXME: Definitely gotta offset for pyrelstd
    for block_ix in range(min(len(old.blocks), len(new.blocks))):
        map_task_ids(old.blocks[block_ix].task, new.blocks[block_ix].task)

    return zip(old.blocks, new.blocks)

def map_task_ids(old: mm.Task|None, new: mm.Task|None):
    if not old or not new:
        return
    for item_ix in range(min(len(old.items), len(new.items))):
        map_action_ids(old.items[item_ix], new.items[item_ix])

def map_action_ids(old: mm.Action|None, new: mm.Action|None):
    if not old or not new:
        return

    if old.action != new.action:
        return

    mapped_props = zip_similar_bindings(old.bindings, new.bindings)
    map_var_ids(old.entity, new.entity)

    for old_property, new_property in mapped_props.items():
        if new_property:
            map_var_ids(old.bindings[old_property], new.bindings[new_property])
        elif not old_property.is_input:
            new.bindings[old_property] = old.bindings[old_property]

    if old.action == mm.ActionType.Get:
        normalize_binding_order(new, (cast(mm.Property, mapped_props.get(prop, prop)) for prop in old.bindings.keys()))

def map_var_ids(old: mm.Var|None, new: mm.Var|None):
    if not old or not new:
        return

    # Such hack, but if the vars aren't in all the same places
    # I think this'll always produce different results.
    new.id = old.id

def zip_similar_bindings(old: dict[mm.Property, mm.Var], new: dict[mm.Property, mm.Var]):
    return {old_prop: next((new_prop for new_prop in new.keys() if new_prop.name == old_prop.name), None) for old_prop in old.keys()}
