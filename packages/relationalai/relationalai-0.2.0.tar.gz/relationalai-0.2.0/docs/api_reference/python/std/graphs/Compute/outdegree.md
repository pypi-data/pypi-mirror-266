# `relational.std.graphs.Compute.outdegree()`

```python
relationalai.std.graphs.Compute.outdegree(node: Producer) -> Expression
```

Returns an [`Expression`](../../../Expression.md) that produces the
[outdegree](https://en.wikipedia.org/wiki/Directed_graph#Indegree_and_outdegree) values for the producer passed to `node`.
For an undirected graph, the outdegree of a node is the same as its [degree](./degree.md).

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
    alice.set(follows=bob).set(follows=carol)
    bob.set(follows=carol)

# Create a directed graph and add all edges from the Person.follows property.
directed_graph = Graph(model)
directed_graph.Edge.extend(Person.follows)

# Compute the outdegree of each person in the graph.
with model.query() as select:
    person = Person()
    outdegree = directed_graph.compute.outdegree(person)
    response = select(person.name, outdegree)

print(response.results)
# Output:
#     name  v
# 0  Alice  2
# 1    Bob  1
# 2  Carol  0

# In an undirected graph, the outdegree of a node is the same as its degree.
undirected_graph = Graph(model, undirected=True)
undirected_graph.Edge.extend(Person.follows)

with model.query() as select:
    person = Person()
    outdegree = undirected_graph.compute.outdegree(person)
    degree = undirected_graph.compute.degree(person)
    response = select(person.name, outdegree, degree)

print(response.results)
# Output:
#     name  v  v2
# 0  Alice  2   2
# 1    Bob  2   2
# 2  Carol  2   2
```

## See Also

[`Compute.degree()`](./degree.md) and [`Compute.indegree()`](./indegree.md).
