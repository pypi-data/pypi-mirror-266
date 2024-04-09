# `relationalai.std.graphs.Compute.pagerank()`

```python
relationalai.std.graphs.Compute.pagerank(
    node: Producer,
    damping_factor: float = 0.85,
    tolerance: float = 1e-6,
    max_iter: int = 20
) -> Expression
```

Returns an [`Expression`](../../../Expression.md) that produces the
[PageRank](https://en.wikipedia.org/wiki/PageRank) values for the producer passed to `node`.

## Supported Graph Types

| Graph Type | Supported | Notes |
| :--- | :--- | :------ |
| Directed | Yes |   |
| Undirected | Yes |   |

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `node` | [`Producer`](../../../Producer/README.md) | A producer that produces object IDs of nodes. |
| `damping_factor` | `float` | The PageRank damping factor. Must be between 0 and 1, inclusive. Default is 0.85. |
| `tolerance` | `float` | The convergence tolerance for the PageRank algorithm. Default is 1e-6. |
| `max_iter` | `int` | The maximum number of iterations allowed in the PageRank algorithm. Default is 20. |

## Returns

An [`Expression`](../../../Expression.md) object that produces `float` values.

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

# Create a graph and add all Person objects to the set of nodes
# and the Person.follows property to the set of edges.
graph = Graph(model)
graph.Node.extend(Person)
graph.Edge.extend(Person.follows)

# Compute the PageRank of each person in the graph.
with model.query() as select:
    person = Person()
    centrality = graph.compute.pagerank(person)
    response = select(person.name, centrality)

print(response.results)
# Output:
#     name         v
# 0  Alice  0.397402
# 1    Bob  0.214806
# 2  Carol  0.387792
```

## See Also

[`Compute.betweenness_centrality`](./betweenness_centrality.md)
and [`Compute.degree_centrality`](./degree_centrality.md).
