# `relationalai.Producer.__ne__()`

```python
relationalai.Producer.__ne__(other: Any) -> Expression
```

Returns an [`Expression`](../Expression.md) that restricts [`Producer`](./README.md) to values not equal to `other`.

#### Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `other` | `Any` | A numeric value or another `Producer` object. |

#### Returns

An [`Expression`](../Expression.md) object.

#### Example

The `Producer.__ne__()` method is called when you use the `!=` operator with a `Producer` object:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    Person.add(name="Fred", age=39)
    Person.add(name="Wilma", age=36)

with model.query() as select:
    person = Person()
    # Restrict `person.age` to values that are equal to 36.
    # `person.age` returns an `InstanceProperty` object,
    # which is also a `Producer` object.
    person.age != 36
    response = select(person.name, person.age)

print(response.results)
# Output:
#    name  age
# 0  Fred   39
```

You may use `!=` with two `Producer` objects:

```python
with model.query() as select:
    person1, person2 = Person(), Person()
    person1.age != person2.age
    response = select(person1.name, person2.name)

print(response.results)
# Output:
#     name  name2
#     name  name2
# 0   Fred  Wilma
# 1  Wilma   Fred
```

#### See Also

[`Producer.__eq__()`](./eq__.md)
