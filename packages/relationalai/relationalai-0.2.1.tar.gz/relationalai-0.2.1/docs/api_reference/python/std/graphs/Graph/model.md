# `relationalai.std.graphs.Graph.model`

An attribute assigned to the [model](../../../Model/README.md) to which a [`Graph`](../Graph/README.md) belongs.

## Returns

A [`Model`](../../../Model/README.md) object.

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
    alice.set(follows=bob)

# Create a graph.
graph = Graph(model)
graph.Node.extend(Person)
graph.Edge.extend(Person.follows)

print(graph.model == model)
# Output:
# True
```
