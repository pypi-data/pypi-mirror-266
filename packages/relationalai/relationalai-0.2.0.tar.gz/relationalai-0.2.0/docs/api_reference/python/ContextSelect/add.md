# `relationalai.ContextSelect.add()`

```python
relationalai.ContextSelect.add(item: Any, **kwargs: Any) -> None
```

Adds an item to a [`ContextSelect`](./README.md) object.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `item` | `Any` | The item to be added to the collection. |
| `kwargs` | `Any` | Optional keyword arguments that set context-specific properties on items in the collection. |

## Returns

`None`

## Example

```python
import relationalai as rai

model = rai.Model("books")
Book = model.Type("Book")

# Add some books to the model.
with model.rule():
    Book.add(title="Foundation", author="Isaac Asimov", year=1951)
    Book.add(title="Humble Pi", author="Matt Parker", year=2019)

# Get all books authored by Isaac Asimov or published after 1950.
with model.query() as select:
    book = Book()
    with model.union() as union:
        with book.author == "Isaac Asimov":
            union.add(book, message="authored by Asimov")
        with book.year > 1950:
            union.add(book, message="published after 1950")
    response = select(union.title, union.author, union.message)

print(response.results)
# Output:
#         title        author                     v
# 0  Foundation  Isaac Asimov    authored by Asimov
# 1  Foundation  Isaac Asimov  published after 1950
# 2   Humble Pi   Matt Parker  published after 1950
```

Here, `union` is a `ContextSelect` object returned by the
[`model.union().__enter__()`](../Context/enter__.md) method.

Only `with` statements may appear in a `Model.union()` context.
Each `with` statement describes a condition that necessitates inclusion in the union
and calls `union.add()` to add an object to the union.
The preceding example adds books authored by Isaac Asimov and books published after 1950 to `union`.

The `message` keyword argument adds a `message` property to objects in `union`.
Multiple `message` values are set on objects for which multiple conditions apply.
Properties added to items in a `ContextSelect` are properties of the `ContextSelect` object, _not_ the item.
The `union` object has the `message` property in the preceding example, not `Book` objects.

Calling `.add()` on the same `ContextSelect` object with different keyword arguments raises an exception.
Since `.add()` sets a `message` property the first time it's called in the preceding example,
so must the second call to `.add()`.

Note that the column for the `.message` property in the results has the generic name `v`.
You may change the column name using [`relationalai.std.alias()`](../std/alias.md):

```python
from relationalai.std import alias

with model.query() as select:
    book = Book()
    with model.union() as union:
        with book.author == "Isaac Asimov":
            union.add(book, message="authored by Asimov")
        with book.year > 1950:
            union.add(book, message="published after 1950")
    response = select(
        union.title, union.author, alias(union.message, "message")
    )

print(response.results)
# Output:
#         title        author               message
# 0  Foundation  Isaac Asimov    authored by Asimov
# 1  Foundation  Isaac Asimov  published after 1950
# 2   Humble Pi   Matt Parker  published after 1950
```

## See Also

[`ContextSelect.__getattribute__()`](./getattribute__.md),
[`Model.ordered_choice()`](../Model/ordered_choice.md),
and [`Model.union()`](../Model/union.md)
