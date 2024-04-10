<!-- markdownlint-disable MD024 -->

# `Type`

Types are collections of objects.
You create types using the [`Model.Type()`](../Model/Type.md) method,
which returns an instance of the `Type` class.

```python
class relationalai.Type(model: Model, name: str)
```

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `model` | [`Model`](../Model/README.md) | The model in which the type is created. |
| `name` | `str` | The name of the type. Type names must begin with a Unicode letter or an underscore followed by one or more Unicode letters, underscores, or numbers. |

## Attributes

- [`Type.model`](./model.md)
- [`Type.name`](./name.md)

## Methods

- [`Type.__call__()`](./call__.md)
- [`Type.__or__()`](./or__.md)

## Example

Use [`Model.Type()`](../Model/Type.md) to create a `Type` object rather than constructing one directly:

```python
import relationalai as rai

# Create a new model.
model = rai.Model("myModel")

# Create a new type.
MyType = model.Type("MyType")
```
