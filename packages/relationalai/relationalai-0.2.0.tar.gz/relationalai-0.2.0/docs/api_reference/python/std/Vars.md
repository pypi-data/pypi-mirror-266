# `relationalai.std.Vars`

```python
relationalai.std.Vars(count: int) -> List[Instance]
```

Create `count` number of [`Instance`](../Instance/README.md) objects representing unknown values
in a [rule](../Model/rule.md) or [query](../Model/query.md).

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `count` | `int` | The number of `Instance` objects to return. |

## Returns

An [`Instance`](../Instance/README.md) object or a `list` of `Instance` objects.

## Example

You must call `Vars()` from within a [rule](../Model/rule.md) or [query](../Model/query.md):

```python
import relationalai as rai
from relationalai.std import Vars

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    Person.add(name="Joe", age=41)
    Person.add(name="Jane", age=39)

with model.query() as select:
    person = Person()
    x = Vars(1)
    person.age == x
    x > 40
    response = select(person.name, x)

print(response.results)
# Output:
#   name   v
# 0  Joe  41
```
