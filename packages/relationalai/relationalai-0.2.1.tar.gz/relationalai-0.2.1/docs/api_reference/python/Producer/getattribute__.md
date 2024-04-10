# `relationalai.Producer.__getattribute__()`

```python
relationalai.Producer.__getattribute__(name: str) -> InstanceProperty | None
```

Restricts the values produced to those for which a property named `name` is set
and returns an [`InstanceProperty`](../InstanceProperty/README.md) object.
`.__getattribute__()` is called whenever you access a property using dot notation, such as `book.title`, or `person.age`.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `name` | `str` | The name of the property to get. |

## Returns

An [`InstanceProperty`](../InstanceProperty/README.md) object,
except for [`Expression`](../Expression.md) objects, in which case `.__getattribute__()` returns `None`.

## Example

It is essential to keep in mind that property access adds a constraint to your context.
For example, the following query only returns objects in `Person` that have a `name` _and_ `age` property:

```python
# Add a person with an age property.
with model.rule():
    Person.add(name="Wilma", age=36)

with model.query() as select:
    person = Person()
    # Restrict `person` to objects with an `age` property.
    person.age
    response = select(person.name)

# Fred is not included in the results because he has no `age` property.
print(response.results)
# Output:
#     name
# 0  Wilma
```

## See Also

[`InstanceProperty`](../InstanceProperty/README.md)
