# `relationalai.std.graphs.Graph.undirected`

An attribute assigned to `True` if the graph is undirected and `False` if it is directed.

## Returns

A `bool` object.

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

# By default, graphs are directed.
print(graph.undirected)
# Output:
# False
```

To create an undirected graph, set the `Graph()` constructor's  `undirected` parameter to `True`:

```python
graph = Graph(model, undirected=True)
graph.Edge.extend(Person.follows)

print(graph.undirected)
# Output:
# True
```
