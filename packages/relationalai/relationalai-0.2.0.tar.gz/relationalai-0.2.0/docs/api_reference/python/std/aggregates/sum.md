# `relationalai.std.aggregates.sum()`

```python
relationalai.std.aggregates.sum(*args: Producer, per: Optional[List[Producer]]) -> Expression
```

Creates an [`Expression`](../../Expression.md) object that produces the sum of the values produced by a [`Producer`](../../Producer/README.md).
Pass a list of one or more `Producer` objects to the optional `per` parameter to group values and compute the sum per group.

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
    age_sum = aggregates.sum(person.age)
    response = select(age_sum)

print(response.results)
# Output:
#     v
# 0  80
```

`person.age` represents the _set_ of all ages in the model.
If two people have the same age, you must pass the `person` instance,
in addition to `person.age`, to `sum()` so that each person contributes to the sum:

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
    age_sum = aggregates.sum(person, person.age)
    response = select(age_sum)

print(response.results)
# Output:
#      v
# 0  121
```

When the [query](../../Model/query.md) is evaluated,
all pairs of `person` objects and their `age` properties are formed, and the sum of the age values is computed.
You may pass any number of [`Producer`](../../Producer/README.md) objects to `sum()`.
The aggregation occurs over the values produced by the last argument.

To group values and compute the sum for each group,
pass one or more `Producer` objects to the optional `per` parameter as a list.
In the following example, the `person` object is passed to `per` to compute the sum of the ages of a person's friends:

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
    friend_age_sum = aggregates.sum(person.friend, person.friend.age, per=[person])
    response = select(person.name, friend_age_sum)

print(response.results)
# Output:
#    name   v
# 0  Jane  41
# 1   Joe  80
# 2  John  41
```

## See Also

[`avg()`]() and [`count()`]().
