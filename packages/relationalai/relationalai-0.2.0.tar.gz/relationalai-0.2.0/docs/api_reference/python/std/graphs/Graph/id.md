# `relationalai.std.graphs.Graph.id`

An attribute assigned to the graph's unique integer ID.

## Returns

An `int` object.

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

# Create a graph and add edges to it from the `Person.follows` property.
graph = Graph(model)
graph.Node.extend(Person)
graph.Edge.extend(Person.follows)

print(graph.id)
# Output:
# 1
```
