# `relationalai.std.aggregates.count()`

```python
relationalai.std.aggregates.count(*args: Producer, per: Optional[List[Producer]]) -> Expression
```

Creates an [`Expression`](../../Expression.md) object that produces the number of values
produced by one or more [Producer](../../Producer/README.md) objects.
Pass a list of `Producer` objects to the optional `per` parameter to group values and count each group.

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
    Person.add(name="John", age=41)

with model.query() as select:
    person = Person()
    num_people = aggregates.count(person)
    response = select(num_people)

print(response.results)
# Output:
#    result
# 0       3
```

Take care when counting properties that may have multiple values.
`.count()` counts the number of unique values represented by a `Producer`.
For instance, there are two age values, not three, since two people are the same age:

```python
with model.query() as select:
    person = Person()
    num_ages = aggregates.count(person.age)
    response = select(num_ages)

print(response.results)
# Output:
#    result
# 0       2
```

You may pass multiple `Producer` objects to `count()`:

```python
with model.query() as select:
    person = Person()
    num_person_age_pairs = aggregates.count(person, person.age)
    response = select(num_person_age_pairs)

print(response.results)
# Output:
#    result
# 0       3
```

When you pass both `person` and `person.age`, `count()` counts the number of _pairs_ of people and their ages.
`count()` supports any number of arguments.

To group values and count the number of values in each group,
pass one or more `Producer` objects to the optional `per` parameter as a list.
In the following example, the `person` object is passed to `per` to count the number of friends each person has:

```python
import relationalai as rai
from relationalai.std import aggregates

model = rai.Model("friends")
Person = model.Type("Person")

with model.rule():
    joe = Person.add(name="Joe")
    jane = Person.add(name="Jane")
    john = Person.add(name="John")
    joe.set(friend=jane).set(friend=john)
    jane.set(friend=joe)
    john.set(friend=joe)

with model.query() as select:
    person = Person()
    friend_count = aggregates.count(person.friend, per=[person])
    response = select(person.name, friend_count)

print(response.results)
# Output:
#    name  result
# 0  Jane       1
# 1   Joe       2
# 2  John       1
```

## See Also

[`avg()`](./avg.md),
[`max()`](./max.md),
[`min()`](./min.md),
and [`sum()`](./sum.md).
