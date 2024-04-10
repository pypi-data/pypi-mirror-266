# `relationalai.ContextSelect.__getattribute__()`

```python
relationalai.ContextSelect.__get_attribute__(name: str) -> Instance
```

Gets an [`InstanceProperty`](../InstanceProperty/README.md) representing the property called `name` of
objects contained in the `ContextSelect` object.
Properties may be those created with [`Type.add()`](../Type/add.md)
or [`ContextSelect.add()`](./add.md).

#### Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `name` | `str` | The name of the property to get. |

#### Returns

An [`Instance`](../Instance/README.md) object.

#### Example

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
    # Select the `.title`, `.author`, and `.message` properties of
    # objects in `union`. Note that `.title` and `.author` were created
    # by `Book.add()`, whereas `.message` was created by `union.add()`.
    response = select(union.title, union.author, union.message)

print(response.results)
# Output:
#         title        author                     v
# 0  Foundation  Isaac Asimov    authored by Asimov
# 1  Foundation  Isaac Asimov  published after 1950
# 2   Humble Pi   Matt Parker  published after 1950
```

#### See Also

[`Model.ordered_choice()`](../Model/ordered_choice.md) and [`Model.union()`](../Model/union.md).
