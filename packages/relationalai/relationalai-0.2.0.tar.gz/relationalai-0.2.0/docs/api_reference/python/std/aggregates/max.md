# `relationalai.std.aggregates.max()`

```python
relationalai.std.aggregates.max(*args: Producer, per: Optional[List[Producer]]) -> Expression
```

Creates an [`Expression`](../../Expression.md) object that produces the maximum of
the values produced by one or more [`Producer`](../../Producer/README.md) objects.
Pass a list of `Producer` objects to the optional `per` parameter to group values and compute the maximum value per group.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `*args` | [`Producer`](../../Producer/README.md) | One or more [`Producer`](../../Producer/README.md) objects. |

## Returns

An [`Expression`](../../Expression.md) object.

## Example

```python
import relationalai as rai
from relationalai.std import aggregates

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    Person.add(name="Joe", age=39)
    Person.add(name="Jane", age=40)

with model.query() as select:
    person = Person()
    max_age = aggregates.max(person.age)
    response = select(max_age)

print(response.results)
# Output:
#    result
# 0      40
```

To group values and compute the maximum for each group,
pass one or more `Producer` objects to the optional `per` parameter as a list.
In the following example, the `person` object is passed to `per` to compute the maximum age of a person's friends:

```python
import relationalai as rai
from relationalai.std import aggregates

model = rai.Model("friends")
Person = model.Type("Person")

with model.rule():
    joe = Person.add(name="Joe", age=39)
    jane = Person.add(name="Jane", age=40)
    john = Person.add(name="John", age=41)
    joe.set(friend=jane).set(friend=john)
    jane.set(friend=joe)
    john.set(friend=joe)

with model.query() as select:
    person = Person()
    max_friend_age = aggregates.max(person.friend.age, per=[person])
    response = select(person.name, max_friend_age)

print(response.results)
# Output:
#    name  result
# 0  Jane      39
# 1   Joe      41
# 2  John      39
```

## See Also

[`avg()`](./avg.md) and [`min()`](./min.md).
