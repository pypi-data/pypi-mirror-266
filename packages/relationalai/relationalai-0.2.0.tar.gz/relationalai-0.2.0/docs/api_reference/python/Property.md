<!-- markdownlint-disable MD024 -->

# `relationalai.Property`

Properties are [producers](./Producer/README.md) that produce property values of [types](./Type/README.md).
You do not create `Property` objects directly.
They are created when you access the property as an attribute on a type.

```python
class Property(model: Model)
```

The `Property` class is a subclass of [`Producer`](./Producer/README.md).

## Parameters

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `model` | [`Model`](./Model/README.md) | The model to which the property belongs. |

## Example

You do not create `Property` objects directly.
Accessing a property as a [`Type`](./Type/README.md) attribute returns a `Property` object:

```python
import relationalai as rai

model = rai.Model("books")
Book = model.Type("Book")

with model.rule():
    Book.add(title="Foundation", author="Isaac Asimov")

print(type(Book.title))
# Output:
# <class 'relationalai.dsl.Property'>

with model.query() as select:
    response = select(Book.title, Book.author)

print(response.results)
```

`Property` objects are `Producer` objects and support the same attributes and methods.
See [`Producer`](./Producer/README.md) for details.

However, `Property` objects may not be used as variables in a rule or query.
Doing so will raise and exception:

```python
with model.query() as select:
    title = Book.title
    author = Book.author
    title == "Foundation"  # This raises an exception.
    response = select(author) # This also raises an exception.
```

`Property` objects may be passed as arguments to [`std.graphs.Edges.extend()`](./std/graphs/Edges/extend.md)
in order to add the relationships defined by a property as edges to a [`Graph`](./std/graphs/Graph/README.md).

## See Also

[`Producer`](./Producer/README.md) and [`InstanceProperty`](./InstanceProperty/README.md).
