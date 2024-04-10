# `relationalai.std.graphs.Nodes`

The `Nodes` class represents the collection of nodes in a graph.
You do not create `Nodes` objects directly.
A `Nodes` instance is automatically instantiated when you create a [`Graph`](../Graph/README.md).
You access a graph's `Nodes` instance via the [`Graph.nodes`](../Graph/nodes.md) attribute.

```python
class relationalai.std.graphs.Nodes(graph: Graph)
```

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `graph` | [`Graph`](../Graph/README.md) | The graph on which the `Nodes` object is instantiated. |

## Methods

- [`Nodes.add()`](./add.md)
- [`Nodes.extend()`](./extend.md)

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

# Create a graph and get the set of nodes.
graph = Graph(model)
nodes = graph.nodes

# Add the `Person` type to the set of nodes.
nodes.extend(Person)
```
