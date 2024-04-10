# `relationalai.Context.__enter__()`

```python
relationalai.Context.__enter__() -> ContextSelect
```

[`Context`](./re) objects are [context managers](https://docs.python.org/3/glossary.html#term-context-manager).
Although you can call the `.__enter__()` method directly, it is typically called by a
[`with` statement](https://docs.python.org/3/reference/compound_stmts.html#with).

In a `with` statement, Python calls the context manager's `.__enter__()` method before executing the `with` block.
Optionally, you may give the [`ContextSelect`](../ContextSelect/README.md) object returned by `.__enter__()` a name
in the `as` part of the `with` statement.
After the `with` block executes,
the `with` statement automatically executes the [`Context.__exit__()`](./exit__.md) method.

## Returns

A [`ContextSelect`](../ContextSelect/README.md) object.

## Example

You create rule contexts with [`Model.rule()`](../Model/rule.md)
and query contexts with [`Model.query()`](../Model/query.md).
The `Model.query()` context's `.__enter__()` method returns a [`ContextSelect`](../ContextSelect/README.md) object,
typically given the name `select`, that you use to select query results:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

# The `with` statement calls the `model.rule()` context's
# `.__enter__()` method automatically. The `ContextSelect` object
# returned by `.__enter__()` is not typically used in a rule.
with model.rule():
    Person.add(name="Fred")

# The `with` statement calls the `model.query()` context's
# `.__enter__()` method and assigns the `ContextSelect`
# object it returns to a Python variable named `select`.
with model.query() as select:
    person = Person()
    response = select(person.name)

print(response.results)
# Output:
#    name
# 0  Fred
```

[Calling `select`](../ContextSelect/call__.md) returns the same `Context` object created by
[`model.query()`](../Model/query.md) in the `with` statement.
The results of the query are stored as a pandas DataFrame
and are accessible via the [`Context.results`](./results.md) attribute.

## See Also

[`Context.__exit__()`](exit__.md) and [`ContextSelect`](../ContextSelect/README.md).
