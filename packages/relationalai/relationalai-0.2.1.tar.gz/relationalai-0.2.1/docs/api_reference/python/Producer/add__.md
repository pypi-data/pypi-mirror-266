# `relationalai.Producer.__add__()`

```python
relationalai.Producer.__add__(other: Any) -> Expression
```

Returns an [`Expression`](../Expression.md) that produces the sum of the [`Producer`](./README.md) values and `other`.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `other` | `Any` | A numeric value or another `Producer` object. |

## Returns

An [`Expression`](../Expression.md) object.

## Example

You may sum a `Producer` with a number literal:

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
    age_after_next_birthday = person.age + 1
    response = select(person.name, age_after_next_birthday)

print(response.results)
# Output:
#     v
#     name   v
# 0   Fred  40
# 1  Wilma  37
```

You may also sum two `Producer` objects:

```python
with model.rule():
    fred = Person(name="Fred")
    fred.set(cash=100.0, savings=200.0)

with model.rule():
    wilma = Person(name="Wilma")
    wilma.set(cash=90.0, savings=310.0)

with model.query() as select:
    person = Person()
    # `person.cash` and `person.savings` return `InstanceProperty`
    # objects, which are also `Producer` objects.
    total_assets = person.cash + person.savings
    response = select(person.name, total_assets)

print(response.results)
# Output:
#     name      v
# 0   Fred  300.0
# 1  Wilma  400.0
```

## See Also

[`Producer.__mul__()`](./mul__.md),
[`Producer.__pow__()`](./pow__.md),
[`Producer.__sub__()`](./sub__.md),
and [`Producer.__truediv__()`](./truediv__.md).
