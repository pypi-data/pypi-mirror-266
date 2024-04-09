# `relationalai.std.graphs.Compute.betweenness_centrality()`

```python
relationalai.std.graphs.Compute.betweenness_centrality(node: Producer) -> Expression
```

Returns an [`Expression`](../../../Expression.md) that produces the
[betweenness centrality](https://en.wikipedia.org/wiki/Betweenness_centrality) values
for the producer passed to `node`.

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

# Compute the betweenness centrality of each person in the graph.
with model.query() as select:
    person = Person()
    centrality = graph.compute.betweenness_centrality(person)
    response = select(person.name, centrality)

print(response.results)
# Output:
#     name    v
# 0  Alice  1.0
# 1    Bob  0.0
# 2  Carol  1.0
```

## See Also

[`Compute.degree_centrality`](./degree_centrality.md) and [`Compute.pagerank`](./pagerank.md).
