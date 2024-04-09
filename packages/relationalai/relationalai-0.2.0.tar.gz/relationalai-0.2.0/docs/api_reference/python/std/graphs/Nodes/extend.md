# `relationalai.std.graphs.Nodes.extend()`

```python
relationalai.std.graph.Node.extend(type: Type, **kwargs: Any) -> None
```

Add all objects in a [`Type`](../../../Type/README.md) to the graph's nodes.
Node properties may be passed as keyword arguments to `**kwargs`.
You can use and display these properties in graph visualizations.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `type` | [`Type`](../../../Type/README.md) | The `Type` containing the objects to add to the graph's nodes. |
| `**kwargs` | `Any` | Keyword arguments representing property name and value pairs. Values may be literals or `Producer` objects. |

## Returns

`None`.

## Example

```python
import relationalai as rai
from relationalai.std.graphs import Graph

# Create a model with a `Person` type.
model = rai.Model("socialNetwork")
Person = model.Type("Person")

# Add some people to the model and connect them with a `follows` property.
with model.rule():
    Person.add(name="Alice")
    Person.add(name="Bob")

# Create a graph and extend the nodes with the `Person` type.
graph = Graph(model)
graph.Node.extend(Person)
```

## See Also

[`Edges.add()`](./add.md) and [`Graph.nodes`](../Graph/nodes.md).
