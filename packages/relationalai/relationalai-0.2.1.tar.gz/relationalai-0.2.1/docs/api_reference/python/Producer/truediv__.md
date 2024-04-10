# `relationalai.Producer.__truediv__()`

```python
relationalai.Producer.__truediv__(other: Any) -> Expression
```

Returns an [`Expression`](../Expression.md) that produces the quotient of the [`Producer`](./README.md) values and `other`.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `other` | `Any` | A numeric value or another `Producer` object. |

## Returns

An [`Expression`](../Expression.md) object.

## Example

A `Producer` object may be divided by a numeric literal:

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
    # which is also a `Producer` object.
    percent_life_completed = person.age / 76
    response = select(person.name, percent_life_completed)

print(response.results)
# Output:
#     v
#     name         v
# 0   Fred  0.513158
# 1  Wilma  0.473684
```

You may also divide two `Producer` objects:

```python
with model.rule():
    fred = Person(name="Fred")
    fred.set(savings=200.0, savings_goal=1000.0)

with model.rule():
    wilma = Person(name="Wilma")
    wilma.set(savings=300.0, savings_goal=500.0)

with model.query() as select:
    person = Person()
    # `person.savings`, and `person.savings_goal`return
    # `InstanceProperty` objects, which are also `Producer` objects.
    percent_goal_completed = savings / savings_goal
    response = select(person.name, percent_goal_completed)

print(response.results)
# Output:
#     name    v
# 0   Fred  0.2
# 1  Wilma  0.6
```

## See Also

[`Producer.__add__()`](./add__.md),
[`Producer.__mul__()`](./mul__.md),
[`Producer.__pow__()`](./pow__.md),
and [`Producer.__sub__()`](./sub__.md).
