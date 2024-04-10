# `relationalai.InstanceProperty.or_()`

```python
relationalai.InstanceProperty.or_(other: Any) -> InstanceProperty
```

Returns an [`InstanceProperty`](./README.md) that produces the same values as the original `InstanceProperty` as well
the default value `other` for objects on which the property is not set.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `other` | `Any` | The default property value. |

## Returns

An [`InstanceProperty`](./README.md) object.

## Example


```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    Person.add(name="Fred", age=39)
    Person.add(name="Wilma")

with model.query() as select:
    person = Person()
    age = person.age.or_(-1)  # Produce -1 if the person has no age property.
    response = select(person.name, age)

print(response.results)
# Output:
#     name  age
# 0   Fred   39
# 1  Wilma   -1
```

Note that you may put the call to `.or_()` inside of `select` if you wish:

```python
with model.query() as select:
    person = Person()
    response = select(person.name, person.age.or_(-1))
```

Contrast that to the same query without `.or_()`, which does not return a row for Wilma:

```python
with model.query() as select:
    person = Person()
    response = select(person.name, person.age)

print(response.results)
# Output:
#     name  age
# 0   Fred   39
```
