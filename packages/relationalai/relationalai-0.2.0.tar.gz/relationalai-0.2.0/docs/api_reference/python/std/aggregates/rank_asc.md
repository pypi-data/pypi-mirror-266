# `relationalai.std.aggregates.rank_asc()`

```python
relationalai.std.aggregates.rank_asc(*args: Producer, per: Optional[List[Producer]]) -> Expression
```

Creates an [`Expression`](../../Expression.md) object that produces the
ascending sort order of the values produced by one or more [`Producer`](../../Producer/README.md) objects.
Pass a list of `Producer` objects to the optional `per` parameter to group and sort values.

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
    rank = aggregates.rank_asc(person.age)
    response = select(rank, person.name, person.age)

print(response.results)
# Output:
#    v  name  age
# 0  1  Jane   39
# 1  2   Joe   41
```

`person.age` produces the _set_ of all ages in the model.
If two people have the same age, you must pass the `person` instance to `rank_asc()`,
in addition to `person.age`, so that each person, not just their age, is sorted:

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
    rank = aggregates.rank_asc(person.age, person)
    response = select(rank, person.name, person.age)

print(response.results)
# Output:
#    v  name  age
# 0  1  Jane   39
# 1  2  John   41
# 2  3   Joe   41
```

When the [query](../../Model/query.md) is evaluated,
all pairs of `person` objects and their `age` properties are sorted.
You may pass any number of [`Producer`](../../Producer/README.md) objects to `rank_asc()`,
which sorts the set of values in ascending [lexicographic order](https://en.wikipedia.org/wiki/Lexicographic_order)
by column.

To group and sort values, pass one or more `Producer` objects as a list to the optional `per` parameter.
In the following example, the `person` object is passed to `per` to sort each person's friends by age:

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
    friend_rank = aggregates.rank_asc(
        person.friend.age, person.friend, per=[person]
    )
    response = select(
        person.name, friend_rank, person.friend.name, person.friend.age
    )

print(response.results)
# Output:
#    name  v name2  age
# 0  Jane  1   Joe   41
# 1   Joe  1  Jane   39
# 2   Joe  2  John   41
# 3  John  1   Joe   41
```

## See Also

[`rank_desc()`](./rank_desc.md).
