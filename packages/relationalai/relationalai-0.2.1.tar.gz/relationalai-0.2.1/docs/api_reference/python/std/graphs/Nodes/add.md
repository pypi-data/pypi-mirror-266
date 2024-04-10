# `relationalai.std.graphs.Nodes.add()`

```python
relationalai.std.graph.Node.add(node: Producer, **kwargs: Any) -> None
```

Adds objects produced by the `node` producer to the graph's nodes.
Node properties may be passed as keyword arguments to `**kwargs`.
You can use and display these properties in graph visualizations.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `node` | [`Producer`](../../../Producer/README.md) | A producer that produces nodes. |
| `**kwargs` | `Any` | Keyword arguments representing property name and value pairs. Values may be literals or `Producer` objects. |

## Returns

`None`.

## Example

```python
import relationalai as rai
from relationalai.std.graphs import Graph

# Create a model with `Person` and `Transaction` types.
model = rai.Model("socialNetwork")
Person = model.Type("Person")

# Add some people to the model.
with model.rule():
    Person.add(name="Alice")
    Person.add(name="Bob")

# Create a graph.
graph = Graph(model)

# Add people to the graph's nodes.
with model.rule():
    person = Person()
    graph.Node.add(person, name=person.name)
```

## See Also

[`Nodes.extend()`](./extend.md) and [`Graph.nodes`](../Graph/nodes.md).
