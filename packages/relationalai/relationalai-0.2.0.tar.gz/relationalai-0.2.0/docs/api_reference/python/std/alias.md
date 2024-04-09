# `relationalai.std.alias`

```python
relationalai.std.alias(ref: Producer, name: str) -> Var
```

Rename `ref` so that it appears with the alias `name` in query results.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `ref` | [`Producer`](../Producer/README.md) | The object to be aliased. |
| `name` | `str` | The name to use as the alias. |

## Returns

A `Var` object.

## Example

```python
import relationalai as rai
from relationalai.std import alias

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    Person.add(name="Joe")

with model.query() as select:
    person = Person()
    response = select(person.name)

print(response.results)
# Output:
#     name  <-- Column name is the property name
# 0   Alex

# You can change the default column name with `.alias()`.
with model.query() as select:
    person = Person()
    response = select(alias(person.name, "my_col"))

print(response.results)
# Output:
#     my_col
# 0     Alex
```
