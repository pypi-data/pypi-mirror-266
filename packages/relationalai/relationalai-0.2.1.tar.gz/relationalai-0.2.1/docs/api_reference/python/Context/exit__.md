# `relationalai.Context.__exit__()`

```python
relationalai.Context.__exit__(*args) -> None
```

`Context` objects are [context managers](https://docs.python.org/3/glossary.html#term-context-manager).
Although you can call the `.__exit__()` method directly, it is typically called by a
[`with` statement](https://docs.python.org/3/reference/compound_stmts.html#with).

In a `with` statement, Python calls the context manager's [`.__enter__()`](./enter__.md) method
before executing the `with` block.
After the `with` block executes, the `with` statement automatically executes the `.__exit__()` method.
`.__exit__()` translates query builder code inside the `with` block into a RelationalAI query.

## Returns

`None`

## Example

The `.__exit__()` method is called automatically in a `with` statement:

```python
import relationalai as rai

model = rai.Model("people")
Person = model.Type("Person")

# The `with` statement calls the `model.rule()` context's `.__exit__()`
# method automatically after the `with` block terminates.
# `.__exit__()` translates the query builder code into a RelationalAI query.
with model.rule():
    Person.add(name="Fred")

# The `with` statement calls the `model.query()` context's `.__exit__()`
# method automatically after the `with` block terminates.
# `.__exit__()` translates the query builder code into a RelationalAI query,
# sends the query to RelationalAI, and blocks until the results are returned.
with model.query() as select:
    person = Person()
    response = select(person.name)

print(response.results)
# Output:
#    name
# 0  Fred
```

## See Also

[`Context.__enter__()`](./enter__.md)
