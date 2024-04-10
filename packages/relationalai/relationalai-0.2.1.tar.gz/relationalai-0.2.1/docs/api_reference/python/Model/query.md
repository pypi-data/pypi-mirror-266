# `relationalai.Model.query()`

```python
relationalai.Model.query(dynamic: bool = False) -> Context
```

Creates a query [`Context`](../Context/README.md).

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `dynamic` | `bool` | Whether or not the query is dynamic. Dynamic queries support Python control flow as macros. See [`Context`](../Context/README.md) for more information. |

## Returns

A [`Context`](../Context/README.md) object.

## Example

`Model.query()` is a [context manager](https://docs.python.org/3/glossary.html#term-context-manager)
and should be called in a `with` statement.
Use the `as` part of the `with` statement to assign the [`ContextSelect`](../ContextSelect/README.md) object
created by `Model.query()` to a variable named `select` so that you may select query results:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

# Add people to the model.
with model.rule():
    alex = Person.add(name="Alex", age=19)
    bob = Person.add(name="Bob", age=47)
    carol = Person.add(name="Carol", age=17)

# A `with model.query() as select` block begins a new query.
# `select` is a `ContextSelect` object used to select query results.
with model.query() as select:
    person = Person()
    response = select(person.name)

print(response.results)
# Output:
#     name
# 0   Alex
# 1    Bob
# 2  Carol
```

You write queries using RelationalAI's declarative query builder syntax.
See [Getting Started with RelationalAI](../../../getting_started.md) for an introduction to writing queries.

Note that you may pass data from your Python application into a query:

```python
name_to_find = "Carol"
property_to_find = "age"

with model.query() as select:
    person = Person(name=name_to_find)
    prop = getattr(person, property_to_find)
    response = select(prop)

print(response.results)
# Output:
#    age
# 0   17
```

Here, the Python variables `name_to_find` and `property_to_find` are used directly in the query.
Python's built-in [`getattr()`](https://docs.python.org/3/library/functions.html#getattr) function
gets the `person` property with the name `property_to_find`.

By default, queries do not support `while` and `for` loops and other flow control tools such as `if` and
[`match`](https://docs.python.org/3/tutorial/controlflow.html#match-statements).
You can enable flow control by setting the `dynamic` parameter to `True`,
which lets you use Python flow control as a macro to build up a query dynamically:

```python
# Application is being used by an external user.
IS_INTERNAL_USER = FALSE

with model.query() as select:
    person = Person()
    if not IS_INTERNAL_USER:
        Public(person)
    response = select(person.name, person.age)
```

In this query, the application user's state determines whether or not to include a condition.
If the user is external, only `Public` objects are selected.

## See Also

[`Context`](../Context/README.md),
[`ContextSelect`](../ContextSelect/README.md),
and [`Model.rule()`](./rule.md).
