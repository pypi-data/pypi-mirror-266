# `relationalai.Producer.__pow__()`

```python
Producer.__pow__(exp: Any) -> Expression
```

Returns an [`Expression`](../Expression.md) the produces the values of the [`Producer`](./README.md) to the power of `exp`.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `exp` | `Any` | A numeric value or another `Producer` object. |

## Returns

An [`Expression`](../Expression.md) object.

## Example

You may raise a `Producer` object by a number literal:

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
    square_age = person.age ** 2
    response = select(person.name, square_age)

print(response.results)
# Output:
#     name  result
# 0   Fred    1521
# 1  Wilma    1296
```

You may also use a `Producer` as the exponent:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    Person.add(name="Fred", age=39)
    Person.add(name="Wilma", age=36)

with model.query() as select:
    person = Person()
    val = 1.01 ** person.age  # A producer can be the exponent.
    response = select(person.name, val)

print(response.results)
# Output:
#     name    result
# 0   Fred  1.474123
# 1  Wilma  1.430769
```

## See Also

[`Producer.__add__()`](./add__.md),
[`Producer.__mul__()`](./mul__.md),
[`Producer.__sub__()`](./sub__.md),
and [`Producer.__truediv__()`](./truediv__.md).
