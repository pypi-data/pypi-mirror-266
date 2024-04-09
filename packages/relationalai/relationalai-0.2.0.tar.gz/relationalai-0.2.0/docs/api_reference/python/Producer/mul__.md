# `relationalai.Producer.__mul__()`

```python
Producer.__mul__(other: Any) -> Expression
```

Returns an [`Expression`](../Expression.md) the produces the product of the [`Producer`](./README.md) values and `other`.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `other` | `Any` | A numeric value or another `Producer` object. |

## Returns

An [`Expression`](../Expression.md) object.

## Example

You may multiply a `Producer` object by a number literal:

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
    double_age = person.age * 2
    response = select(person.name, double_age)

print(response.results)
# Output:
#     name   v
# 0   Fred  78
# 1  Wilma  72
```

You may also multiply two `Producer` objects:

```python
with model.rule():
    fred = Person(name="Fred")
    fred.set(hours=30.0, wage=20.0)

with model.rule():
    wilma = Person(name="Wilma")
    wilma.set(hours=40.0, wage=30.0)

with model.query() as select:
    person = Person()
    # `person.hours` and `person.wage` return `InstanceProperty`
    # objects, which are also `Producer` objects.
    pay = person.hours * person.wage
    response = select(person.name, pay)

print(response.results)
# Output:
#     name       v
# 0   Fred   600.0
# 1  Wilma  1200.0
```

## See Also

[`Producer.__add__()`](./add__.md),
[`Producer.__pow__()`](./pow__.md),
[`Producer.__sub__()`](./sub__.md),
and [`Producer.__truediv__()`](./truediv__.md).
