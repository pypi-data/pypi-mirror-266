<!-- markdownlint-disable MD024 -->

# `relationalai.ContextSelect`

`ContextSelect` objects are returned by the [`Context.__enter__()`](../Context/__enter__.md_) method.
They are primarily used to select results in [query](../Model/query.md) contexts.
`ContextSelect` objects are also used in [`Model.ordered_choice()`](../Model/ordered_choice.md)
and [`Model.union()`](../Model/union.md) contexts.

```python
class relationalai.ContextSelect(context: Context)
```

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `context` | [`Context`](../Context/README.md) | The `Context` object for which the `ContextSelect` object is created. |

## Methods

- [`ContextSelect.__call__()`](./call__.md)
- [`ContextSelect.__getattribute__()`](./getattribute__.md)
- [`ContextSelect.add()`](./add.md)

## Example

The [`Context.__enter__()`](../Context/enter__.md) method returns a `ContextSelect` object when called
in a [`with` statement](https://docs.python.org/3/reference/compound_stmts.html#with).
An example is the `select` object used in [query](../Model/query.md) contexts:

```python
import relationalai as rai

model = rai.Model("books")
Book = model.Type("Book")

# Add a book to the model.
with model.rule():
    Book.add(title="Foundation", author="Isaac Asimov")
    Book.add(title="Humble Pi", author="Matt Parker")

# Get all books in the model.
# `select` is a `ContextSelect` object returned by `model.query().__enter__()`.
with model.query() as select:
    book = Book()
    response = select(book.name, book.author)

print(response.results)
# Output:
#         title        author
# 0  Foundation  Isaac Asimov
# 1   Humble Pi   Matt Parker
```

`ContextSelect` objects are callable.
The preceding example calls the `select` object to select results in the query.
You may only call `ContextSelect` objects in a [query](../Model/query.md) context.

Other contexts, like [`Model.ordered_choice()`](../Model/ordered_choice.md)
and [`Model.union()`](../Model/union.md), also use a `ContextSelect` object.
In these contexts, the `ContextSelect` object works as a collection of objects:

```python
with model.query() as select:
    book = Book()
    # `union` is a `ContextSelect` object created by the
    # `model.union().__enter__()` method. The `union.add()`
    # method is used to "select" objects based on conditions and
    # add them to the `union` collection.
    with model.union() as union:
        with book.author == "Isaac Asimov":
            union.add(book)
        with book.title == "Humble Pi":
            union.add(book)
    response = select(union.title, union.author)

print(response.results)
# Output:
#         title        author
# 0  Foundation  Isaac Asimov
# 1   Humble Pi   Matt Parker
```

Properties of objects added to a `ContextSelect` object via [`ContextSelect.add()`](./add.md)
may be accessed directly thanks to [`ContextSelect.__getattribute__()`](./getattribute__.md).
For instance, in the preceding example, the `.title` and `.author` properties of
`Book` objects in `union` are accessed as `union.title` and `union.author`.
