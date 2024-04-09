# `relationalai.std.graphs.Graph`

The `Graph` class is used to create graphs representing relationships between objects in a model.
You can use `Graph` objects to perform graph analytics on data in your model.

```python
class relationalai.std.graphs.Graph(model: Model)
```

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `model` | [`Model`](../../../Model/README.md) | The model on which the `Graph` is instantiated. |

## Attributes

- [`Graph.compute`](./compute.md)
- [`Graph.edges`](./edges.md)
- [`Graph.id`](./id.md)
- [`Graph.model`](./model.md)
- [`Graph.nodes`](./nodes.md)
- [`Graph.undirected`](./undirected.md)

## Methods

- [`Graph.fetch()`](./fetch.md)
- [`Graph.visualize()`](./visualize.md)

## Example

```python
import relationalai as rai
from relationalai.std.graphs import Graph

# Create a model with a `Person` type.
model = rai.Model("socialNetwork")
Person = model.Type("Person")

# Add some people to the model and connect them with a `follows` property.
with model.rule():
    alice = Person.add(name="Alice")
    bob = Person.add(name="Bob")
    alice.set(follows=bob)

# Create a graph from the model and visualize it.
graph = Graph(model)
graph.Node.extend(Person, label=Person.name)
graph.Edge.extend(Person.follows)
graph.visualize()
```

![A graph with two nodes labeled Alice and Bob and an edge pointing from Alice to Bob.](./img/simple-social-network.png)