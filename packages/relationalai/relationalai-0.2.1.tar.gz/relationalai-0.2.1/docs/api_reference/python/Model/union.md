# `relationalai.Model.union()`

```python
relationalai.Model.union(dynamic: bool = False) -> Context
```

Creates a [`Context`](../Context/README.md) used to group objects in a rule or query.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `dynamic` | `bool` | Whether or not the context is dynamic. Dynamic queries support Python control flow as macros. See [`Context`](../Context/README.md) for more information. |

## Returns

A [`Context`](../Context/README.md) object.

## Example

`Model.union()` is a [context manager](https://docs.python.org/3/glossary.html#term-context-manager)
and should be called in a `with` statement.
It must be called from within a [rule](./rule.md) or [query](./query.md) context:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    Person.add(name="Alice", age=10)
    Person.add(name="Bob", age=30)
    Person.add(name="Carol", age=60)

# `model.union()` is always called in a nested `with` block
# inside of a `model.rule()` or `model.query()` context.
with model.query() as select:
    person = Person()
    with model.union() as seniors_and_kids:
        # Only `with` statements are allowed directly inside of a `Model.union()` context.
        with person.age >= 60:
            # A `with` block may contain any valid query builder code.
            seniors_and_kids.add(person)
        with person.age < 13:
            seniors_and_kids.add(person)
    response = select(seniors_and_kids.name)

print(response.results)
# Output:
#     name
# 0  Alice
# 1  Carol
```

Here, `seniors_and_kids` is a [`ContextSelect`](../ContextSelect/README.md) object returned by
the `model.union()` context's `.__enter__()` method when the `with` statement is executed.
It behaves similar to a [`Type`](../Type/README.md) in the sense that
`seniors_and_kids` is a collection of objects and has an `.add()` method used to add objects to the collection.
Unlike a `Type`, however, `seniors_and_kids` may only have existing objects added to it.
Moreover, the fact that an object is in `seniors_and_kids` is only retained for the lifetime of the query.

You can use `seniors_and_kids` outside of the `model.union()` block that created it.
Accessing a property from `seniors_and_kids` returns an [`InstanceProperty`](../InstanceProperty/README.md) object that
produces the property values of the objects in the `seniors_and_kids` collection.

You may also add collection-specific properties to objects when they are added to `seniors_and_kids`.
For instance, the following modified query adds a note to each object in the `seniors_and_kids` collection:

```python
with model.query() as select:
    person = Person()
    with model.union() as seniors_and_kids:
        with person.age >= 60:
            seniors_and_kids.add(person, note="senior")
        with person.age < 13:
            seniors_and_kids.add(person, note="kid")
    response = select(seniors_and_kids.name, seniors_and_kids.note)

print(response.results)
# Output:
#     name       v
# 0  Alice     kid
# 1  Carol  senior
```

The `note` property is only accessible from the `seniors_and_kids` object.
Trying to access `person.note` property on `person` will fail,
unless there is already a `note` property for `person` objects.

## See Also

[`Context`](../Context/README.md) and [`Model.ordered_choice()`](./ordered_choice.md).
