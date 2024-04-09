# `relationalai.std.graphs.Compute.eigenvector_centrality()`

```python
relationalai.std.graphs.Compute.eigenvector_centrality(node: Producer) -> Expression
```

Returns an [`Expression`](../../../Expression.md) that produces the
[eigenvector centrality](https://en.wikipedia.org/wiki/Eigenvector_centrality) values
for the producer passed to `node`.

## Supported Graph Types

| Graph Type | Supported | Notes |
| :--- | :--- | :------ |
| Directed | No |   |
| Undirected | Yes |   |

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `node` | [`Producer`](../../../Producer/README.md) | A producer that produces object IDs of nodes. |

## Returns

An [`Expression`](../../../Expression.md) object that produces `float` values.

## Example

```python
import relationalai as rai
from relationalai.std.graphs import Graph

# Create a model named "socialNetwork" with a Person type.
model = rai.Model("socialNetwork")
Person = model.Type("Person")

# Add some people to the model and connect them with a `friend` property.
with model.rule():
    alice = Person.add(name="Alice")
    bob = Person.add(name="Bob")
    carol = Person.add(name="Carol")
    alice.set(friend=carol)
    bob.set(friend=carol)

# Create a graph and add all Person objects to the set of nodes
# and the Person.friend property to the set of edges.
graph = Graph(model, undirected=True)
graph.Edge.extend(Person.friend)

# Compute the eigenvector centrality of each person in the graph.
with model.query() as select:
    person = Person()
    centrality = graph.compute.eigenvector_centrality(person)
    response = select(person.name, centrality)

print(response.results)
# Output:
#     name        v
# 0  Alice  0.57735
# 1    Bob  0.57735
# 2  Carol  0.57735
```

## See Also

[`Compute.betweenness_centrality()`](./betweenness_centrality.md),
[`Compute.degree_centrality()`](./degree_centrality.md),
and [`Compute.pagerank()`](./pagerank.md).
