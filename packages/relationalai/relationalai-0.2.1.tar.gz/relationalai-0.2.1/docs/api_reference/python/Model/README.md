<!-- markdownlint-disable MD024 -->

# `relationalai.Model`

Models represent collections of [objects](../Instance/README.md).
Objects, like Python objects, have [types](../Type/README.md) and [properties](../InstanceProperty/README.md).
Objects may have multiple types, and properties may have multiple values.
You write [rules](../Model/rule.md) to describe objects in your model and the relationships between them
and write [queries](../Model/query.md) to extract data from your model.

Models are instances of the `Model` class.

```python
class relationalai.Model(name: str)
```

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `name` | `str` | The name of the model. Must be at least three characters. May only contain letters, numbers, and underscores. |

## Attributes

- [`Model.name`](./name.md)

## Methods

- [`Model.found()`](./found.md)
- [`Model.not_found()`](./not_found.md)
- [`Model.ordered_choice()`](./ordered_choice.md)
- [`Model.query()`](./query.md)
- [`Model.read()`](./read.md)
- [`Model.rule()`](./rule.md)
- [`Model.scope()`](./scope.md)
- [`Model.Type()`](./Type.md)
- [`Model.union()`](./union.md)

## Example

```python
import relationalai as rai

# Create a new model.
model = rai.Model("myModel")
```
