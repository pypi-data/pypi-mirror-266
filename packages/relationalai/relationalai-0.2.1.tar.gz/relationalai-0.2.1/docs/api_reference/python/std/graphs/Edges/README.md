# `relationalai.std.graphs.Edges`

The `Edges` class represents the collection of edges in a graph.
You do not create `Edges` objects directly.
An `Edges` instance is automatically instantiated when you create a [`Graph`](../Graph/README.md).
You access a graph's `Edges` instance via the [`Graph.edges`](../Graph/edges.md) attribute.

```python
class relationalai.std.graphs.Edges(graph: Graph)
```

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `graph` | [`Graph`](../Graph/README.md) | The graph on which the `Edges` object is instantiated. |

## Methods

- [`Edges.add()`](./add.md)
- [`Edges.extend()`](./extend.md)

## Example

```python
import relationalai as rai
from relationalai.std.graphs import Graph

# Create a model named `socialNetwork` with a `Person` type.
model = rai.Model("socialNetwork")
Person = model.Type("Person")

# Add some people to the model and connect them with a `follows` property.
with model.rule():
    alice = Person.add(name="Alice")
    bob = Person.add(name="Bob")
    carol = Person.add(name="Carol")
    alice.set(follows=carol)
    bob.set(follows=alice)
    carol.set(follows=alice).set(follows=bob)

# Create a graph and get the set of edges.
graph = Graph(model)
Edge = graph.Edge

# Add the `Person.follows` property to the set of edges.
# The nodes in each edge are automatically added to the graph.
Edge.extend(Person.follows)
```
