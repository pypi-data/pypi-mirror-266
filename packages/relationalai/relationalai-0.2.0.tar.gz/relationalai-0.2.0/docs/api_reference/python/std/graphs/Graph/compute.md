# `relationalai.std.graphs.Graph.compute`

An attribute assigned to the graph's [`Compute`](../Compute/README.md) object.

## Returns

A [`Compute`](../Compute/README.md) object.

## Example

A graph's `.compute` object contains methods for computing graph analytical functions on graphs, such as PageRank:

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
graph = Graph(model)
graph.Edge.extend(Person.follows)

# Compute the PageRank of each person in the graph.
with model.query() as select:
    person = Person()
    pagerank = graph.compute.pagerank(person)
    response = select(person.name, pagerank)

print(response.results)
# Output:
#     name         v
# 0  Alice  0.350877
# 1    Bob  0.649123
```

See [`Compute`](../Compute/README.md) for more information.
