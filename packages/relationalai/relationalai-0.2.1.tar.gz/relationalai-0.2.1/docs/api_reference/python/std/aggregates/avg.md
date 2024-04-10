# `relationalai.std.aggregates.avg()`

```python
relationalai.std.aggregates.avg(*args: Producer, per: Optional[List[Producer]]) -> Expression
```

Creates an [`Expression`](../../Expression.md) object that produces the average of
the values produced by one or more [`Producer`](../../Producer/README.md) objects.
Pass a list of `Producer` objects to the optional `per` parameter to group values and compute the average per group.

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
    Person.add(name="Joe", age=41)
    Person.add(name="Jane", age=39)

with model.query() as select:
    person = Person()
    avg_age = aggregates.avg(person.age)
    response = select(avg_age)

print(response.results)
# Output:
#    result
# 0    40.0
```

`person.age` represents the _set_ of all ages in the model.
If two people have the same age, you must pass the `person` instance,
in addition to `person.age`, to `avg()` so that each person contributes to the average:

```python
import relationalai as rai
from relationalai.std import aggregates

model = rai.Model("people")
Person = model.Type("Person")

with model.rule():
    Person.add(name="Joe", age=41)
    Person.add(name="Jane", age=39)
    Person.add(name="John", age=41)

with model.query() as select:
    person = Person()
    avg_age = aggregates.avg(person, person.age)
    response = select(avg_age)

print(response.results)
# Output:
#       result
# 0  40.333333
```

When the [query](../../Model/query.md) is evaluated,
all pairs of `person` objects and their `age` properties are produced, and the average of the age values is computed.
You may pass any number of [`Producer`](../../Producer/README.md) objects to `avg()`.
The aggregation occurs over the values produced by the last argument.

To group values and compute the average for each group,
pass one or more `Producer` objects to the optional `per` parameter as a list.
In the following example, the `person` object is passed to `per` to compute the average age of a person's friends:

```python
import relationalai as rai
from relationalai.std import aggregates

model = rai.Model("friends")
Person = model.Type("Person")

with model.rule():
    joe = Person.add(name="Joe", age=41)
    jane = Person.add(name="Jane", age=39)
    john = Person.add(name="John", age=41)
    joe.set(friend=jane).set(friend=john)
    jane.set(friend=joe)
    john.set(friend=joe)

with model.query() as select:
    person = Person()
    avg_friend_age = aggregates.avg(person.friend, person.friend.age, per=[person])
    response = select(person.name, avg_friend_age)

print(response.results)
# Output:
#    name  result
# 0  Jane    41.0
# 1   Joe    40.0
# 2  John    41.0
```

## See Also

[`max()`](./max.md) and [`min()`](./min.md).
