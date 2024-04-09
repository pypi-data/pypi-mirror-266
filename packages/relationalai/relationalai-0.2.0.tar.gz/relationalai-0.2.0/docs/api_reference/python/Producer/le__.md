# `relationalai.Producer.__le__()`

```python
relationalai.Producer.__le__(other: Any) -> Expression
```

Returns an [`Expression`](../Expression.md) that restricts [`Producer`](./README.md) to values less than or equal to `other`.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `other` | `Any` | A numeric value or another `Producer` object. |

## Returns

An [`Expression`](../Expression.md) object.

## Example

The `Producer.__le__()` method is called when you use the `<=` operator with a `Producer` object:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    Person.add(name="Fred", age=39)
    Person.add(name="Wilma", age=36)

with model.query() as select:
    person = Person()
    # Restrict `person.age` to values that are greater than or equal
    # to 36. `person.age` returns an `InstanceProperty` object,
    # which is also a `Producer` object.
    person.age <= 39
    response = select(person.name, person.age)

print(response.results)
# Output:
#     name  age
# 0   Fred   39
# 1  Wilma   36
```

You may use `<=` with two `Producer` objects:

```python
with model.query() as select:
    person1, person2 = Person(), Person()
    person1.age <= person2.age
    response = select(person1.name, person2.name)

print(response.results)
# Output:
#     name  name2
# 0  Wilma  Fred
```

## See Also

[`Producer.__gt__()`](./gt__.md),
[`Producer.__ge__()`](./ge__.md),
and [`Producer.__lt__()`](./lt__.md).
