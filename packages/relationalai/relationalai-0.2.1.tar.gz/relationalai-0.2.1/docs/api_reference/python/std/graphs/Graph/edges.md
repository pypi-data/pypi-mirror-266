# `relationalai.std.graphs.Graph.edges`

An attribute assigned to the graph's [`Edges`](../Edges/README.md) object.

## Returns

A [`Edges`](../Edges/README.md) object.

## Example

A graph's `.edges` object represents its set of edges:

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

# Create a graph from the model add edges from the `Person.follows` property.
# The nodes from each edge are automatically added to the graph.
graph = Graph(model)
graph.Edge.extend(Person.follows)
```

See [`Edges`](../Edges/README.md) for more information.
