# `relationalai.Model.rule()`

```python
relationalai.Model.rule(dynamic:bool=False) -> Context
```

Creates a rule [`Context`](../Context/README.md).

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `dynamic` | `bool` | Whether or not the rule is dynamic. Dynamic queries support Python control flow as macros. See [`Context`](../Context/README.md) for more information. |

## Returns

A [`Context`](../Context/README.md) object.

## Example

`Model.rule()` is a [context manager](https://docs.python.org/3/glossary.html#term-context-manager)
and should be called in a `with` statement.

Rules describe objects in a model:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")
Adult = model.Type("Adult")

# Add people to the model.
with model.rule():
    alex = Person.add(name="Alex", age=19)
    bob = Person.add(name="Bob", age=47)
    carol = Person.add(name="Carol", age=17)

# All people that are 18 years old or older are adults.
with model.rule() as select:
    person = Person()
    person.age >= 18
    person.set(Adult)
```

You write rules using RelationalAI's declarative query builder syntax.
See [Getting Started with RelationalAI](../../../getting_started.md) for an introduction to writing rules and queries.

Note that you may pass data from your Python application into a rule:

```python
min_adult_age = 21

with model.rule() as select:
    person = Person()
    person.age >= min_adult_age
    person.set(Adult)
```

By default, rules do not support `while` and `for` loops and other flow control tools such as `if` and
[`match`](https://docs.python.org/3/tutorial/controlflow.html#match-statements).
You can enable flow control by setting the `dynamic` parameter to `True`,
which lets you use Python flow control as a macro to build up a rule dynamically:

```python
with model.rule(dynamic=True):
    person = Person()
    for i in range(3):
        person.set(count=i)
```

## See Also

[`Context`](../Context/README.md) and [`Model.query()`](./query.md).
