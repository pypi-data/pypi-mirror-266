<!-- markdownlint-disable MD024 -->

# `relationalai.InstanceProperty`

Instance properties are [producers](./Producer/README.md) that produce property values of objects in a [model](./Model/README.md).
You create properties using the [`Type.add()`](./Type/add.md) and [`Instance.set()`](./Instance/set.md) methods,
which return [`Instance`](./Instance/README.md) objects.
You access properties as [`Instance` attributes](./Producer/getattribute__.md),
which return instances of the `InstanceProperty` class.

```python
class InstanceProperty(model: Model)
```

The `InstanceProperty` class is a subclass of [`Producer`](./Producer/README.md).

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `model` | [`Model`](./Model/README.md) | The model in which the instance property is created. |

## Methods

- [`InstanceProperty.or_()`](./or_.md)

## Example

You do not create `InstanceProperty` objects directly.
Accessing a property as an [`Instance`](./Instance/README.md) attribute returns an `InstanceProperty` object:

```python
import relationalai as rai

model = rai.Model("books")
Book = model.Type("Book")

with model.rule():
    Book.add(title="Foundation", author="Isaac Asimov")

with model.query() as select:
    book = Book()
    # Both `book.author` and `book.name` are `InstanceProperty` objects.
    book.author == "Isaac Asimov"
    response = select(book.name)
```

`InstanceProperty` objects are `Producer` objects and support the same attributes and methods.
See [`Producer`](./Producer/README.md) for details.

## See Also

[`Producer`](./Producer/README.md) and [`Instance`](./Instance/README.md).
