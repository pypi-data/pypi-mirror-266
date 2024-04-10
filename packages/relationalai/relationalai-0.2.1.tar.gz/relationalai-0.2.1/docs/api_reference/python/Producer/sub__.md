# `relationalai.Producer.__sub__()`

```python
relationalai.Producer.__sub__(other: Any) -> Expression
```

Returns an [`Expression`](../Expression.md) that produces the difference between the [`Producer`](./README.md) values and `other`.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `other` | `Any` | A numeric value or another `Producer` object. |

## Returns

An [`Expression`](../Expression.md) object.

## Example

You may subtract a number literal from a `Producer` object:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    Person.add(name="Fred", age=39)
    Person.add(name="Wilma", age=36)

with model.query() as select:
    person = Person()
    # `person.age` returns an `InstanceProperty` object,
    # which are also `Producer` objects.
    years_as_adult = person.age - 18
    response = select(person.name, years_as_adult)

print(response.results)
# Output:
#     name   v
# 0   Fred  21
# 1  Wilma  18
```

You may also subtract two `Producer` objects:

```python
with model.rule():
    fred = Person(name="Fred")
    fred.set(expected_retirement_age=65)

with model.rule():
    wilma = Person(name="Wilma")
    wilma.set(expected_retirement_age=62)

with model.query() as select:
    person = Person()
    # `person.age`, and `person.expected_retirement_age` return
    # `InstanceProperty` objects, which are also `Producer` objects.
    years_to_retirement = person.retirement_age - person.age
    response = select(person.name, years_to_retirement)

print(response.results)
# Output:
#     name   v
# 0   Fred  26
# 1  Wilma  26
```

## See Also

[`Producer.__add__()`](./add__.md),
[`Producer.__mul__()`](./mul__.md),
[`Producer.__pow__()`](./pow__.md),
and [`Producer.__truediv__()`](./truediv__.md).
