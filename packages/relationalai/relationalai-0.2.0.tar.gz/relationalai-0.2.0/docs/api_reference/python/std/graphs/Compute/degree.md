# `relational.std.graphs.Compute.degree()`

```python
relationalai.std.graphs.Compute.degree(node: Producer) -> Expression
```

Returns an [`Expression`](../../../Expression.md) that produces the
[degree](https://en.wikipedia.org/wiki/Degree_(graph_theory)) values for the producer passed to `node`.
For a directed graph, the degree of a node is the sum of its [indegree](./indegree.md) and [outdegree](./outdegree.md).

## Supported Graph Types

| Graph Type | Supported | Notes |
| :--- | :--- | :------ |
| Directed | Yes |   |
| Undirected | Yes |   |

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `node` | [`Producer`](../../../Producer/README.md) | A producer that produces object IDs of nodes. |

## Returns

An [`Expression`](../../../Expression.md) object that produces `int` values.

## Example

```python
import relationalai as rai
from relationalai.std.graphs import Graph

# Create a model named "socialNetwork" with a Person type.
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

# Create an undirected graph and add all Person objects to the set of nodes
# and the Person.follows property to the set of edges.
graph = Graph(model, undirected=True)
graph.Node.extend(Person)
graph.Edge.extend(Person.follows)

# Compute the degree of each person in the graph.
with model.query() as select:
    person = Person()
    degree = graph.compute.degree(person)
    response = select(person.name, degree)

print(response.results)
# Output:
#     name  v
# 0  Alice  2
# 1    Bob  2
# 2  Carol  2

# In a directed graph, the degree of a node is the sum of its indegree and outdegrees.
graph = Graph(model)
graph.Node.extend(Person)
graph.Edge.exted(Person.follows)

with model.query() as select:
    person = Person()
    degree = graph.compute.degree(person)
    response = select(person.name, degree)

print(response.results)
# Output:
#     name  v
# 0  Alice  3
# 1    Bob  2
# 2  Carol  3
```

## See Also

[`Compute.indegree()`](./indegree.md) and [`Compute.outdegree()`](./outdegree.md).
