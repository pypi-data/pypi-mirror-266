# `relationalai.Type.add()`

```python
relationalai.Type.add(self, *args, **kwargs) -> Instance
```

Adds a new object to the type and returns an [`Instance`](../Instance/README.md) representing that object.
Only call `Type.add()` from within a [rule](../Model/rule.md) or [query](../Model/query.md) context.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `*args` | `Any` | Any additional types to which the object being added belongs. |
| `*kwargs` | `Any` | Properties that uniquely identify the object being added. |

## Returns

An [`Instance`](../Instance/README.md) object.

## Example

```python
import relationalai as rai

model = rai.Model("books")

# Create a type named Book.
Book = model.Type("Book")

# Add a book instance to the Book type.
with model.rule():
    Book.add(name="Foundation", author="Isaac Asimov")
```

You may add an object to multiple types simultaneously by passing the type objects as positional parameters:

```python
Fiction = model.type("Fiction")
SciFi = model.Type("SciFi")

with model.rule():
    Book.add(Fiction, SciFi, name="Foundation", author="Isaac Asimov")
```

This rule adds a new book object and classifies it as fiction and sci-fi.

Properties set with `.add()` are hashed internally to uniquely identify the object in the model.
These internal IDs are the values produced by `Instance` objects:

```python
with model.query() as select:
    book = Book()
    reponse = select(book)

print(response.results)
# Output:
#                      book
# 0  iikm1rGdR3jWQtS2XVUZDg
```

## See Also

[`Instanse.set()`](../Instance/set.md)
