# `reltionalai.Producer.__exit__()`

```python
relationalai.Producer.__exit__() -> None
```

[`Producer`](./README.md) objects can be used as [context managers](https://docs.python.org/3/glossary.html#term-context-manager)
in a [`with` statement](https://docs.python.org/3/reference/compound_stmts.html#with)
to apply restrictions in a [rule](../Model/rule.md) or [query](../Model/query.md) conditionally.
In a `with` statement, Python calls the context manager's [`.__enter__()`](./enter__.md)
method before executing the `with` block.
After the `with` block executes, the `with` statement automatically executes the `.__exit__()` method.

See [`Producer.__enter__()`](./enter__.md) for more information.

#### Returns

`None`

#### See Also

[`Producer.__enter__()`](./enter__.md)
