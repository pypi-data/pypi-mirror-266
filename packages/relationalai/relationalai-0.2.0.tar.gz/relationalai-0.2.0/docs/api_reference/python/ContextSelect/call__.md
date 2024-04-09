# `relationalai.ContextSelect.__call__()`

```python
relationalai.ContextSelect.__call__(*args: Producer) -> Context
```

Selects the data to be returned by a query and returns the `ContextSelect` object's [`Context`](../Context/README.md) object.
You may only call `ContextSelect` objects within a [query](../Model/query.md) context.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `*args` | `Producer` | The [producer(s)](../Producer/README.md) to be returned in query results. |

## Returns

A [`Context`](../Context/README.md) object.

## Example

In a [`Model.query()`](../Model/query.md) context, the `ContextSelect` object returned by
[`Model.query().__enter__()`](../Context/enter__.md) is called inside the `with` block
to select query results:

```python
import relationalai as rai

model = rai.Model("books")
Book = model.Type("Book")

# Add a book to the model.
with model.rule():
    Book.add(name="Foundation", author="Isaac Asimov")

# Get the names of all of the books in the model.
# `select` is a `ContextSelect` object and it is called to return the
# `book.name` property for each book found by the query.
with model.query() as select:
    book = Book()
    response = select(book.name)

print(response.results)
# Output:
#         title        author
# 0  Foundation  Isaac Asimov
```

## See Also

[`Context.__enter__()`](../Context/enter__.md) and [`Model.query()`](../Model/query.md).
