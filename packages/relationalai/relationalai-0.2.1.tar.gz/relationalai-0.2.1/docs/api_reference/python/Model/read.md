# `relationalai.Model.read()`

```python
relationalai.Model.read(name: str, dynamic: bool = False) -> Context
```

Creates a [context manager](https://docs.python.org/3/glossary.html#term-context-manager) for reading data from
a resource uploaded with the [`imports:snapshot`](../../cli/README.md#importssnapshot) CLI command.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `name` | `str` | The name of the resource to read. Resources must first be imported using the [`rai imports:snapshot`](../../cli/README.md#importssnapshot) command. |
| `dynamic` | `bool` | Whether or not the context is dynamic. Dynamic contexts support Python control flow as macros. See [`Context`](./Context/README.md) for more information. |

## Returns

A Python [context manager](https://docs.python.org/3/glossary.html#term-context-manager) object.

## Example

Pass a resource name to `model.read()` to create objects from the data in the resource:

```python
import relationalai as rai

model = rai.Model("myModel")
Transaction = model.Type("Transaction")

# Create `Transaction` objects from the rows of the "transactions.csv" resource.
with model.read("transactions.csv") as row:
    # Columns, like `id`, are accessed as attributes of the `row` object.
    transaction = Transaction.add(id=row.id)
    # If a column name is a Python keyword, such as the `from` column, use `getattr()`.
    transaction.set(
        date=row.date,
        from_=getattr(row, "from"),
        to=row.to
    )
```

> [!IMPORTANT]
> Use the `[rai imports:snapshot`](../../cli/README.md#importssnapshot) CLI command to import resources before calling `model.read()`.

`model.read()` behaves like a [`Context`] object.
In particular, dynamic `model.read()` blocks are supported.
See [`model.rule()`](./rule.md) and [`model.query()`](./query.md) for examples of dynamic contexts.

## See Also

[`Context`](./Context/README.md) and [`imports:snapshot`](../../cli/README.md#importssnapshot).
