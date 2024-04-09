# `relationalai.std.graphs.Compute`

The `Compute` class serves as a namespace for graph functions.
You do not create `Compute` objects directly.
A `Compute` instance is automatically instantiated when you create a [`Graph`](../Graph/README.md) object.
You access a graph's `Compute` instance via the [`Graph.compute`](../Graph/compute.md) attribute.

```python
class relationalai.std.graphs.Compute(graph: Graph)
```

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `graph` | [`Graph`](../Graph/README.md) | The graph on which the `Compute` namespace is instantiated. |

## Methods

- [`Compute.betweeness_centrality()`](./betweeness_centrality.md)
- [`Compute.cosine_similarity()`](./cosine_similarity.md)
- [`Compute.degree()`](./degree.md)
- [`Compute.degree_centrality()`](./degree_centrality.md)
- [`Compute.eigenvector_centrality()`](./eigenvector_centrality.md)
- [`Compute.indegree()`](./indegree.md)
- [`Compute.label_propagation()`](./label_propagation.md)
- [`Compute.louvain()`](./louvain.md)
- [`Compute.outdegree()`](./outdegree.md)
- [`Compute.pagerank()`](./pagerank.md)
- [`Compute.weakly_connected_component()`](./weakly_connected_component.md)

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

# Create a graph and add the `Person.follows` property to the set of edges.
graph = Graph(model)
graph.Edge.extend(Person.follows)

# Compute the PageRank of each person in the graph.
with model.query() as select:
    person = Person()
    # The `pagerank` function is in the `graph.compute` namespace.
    pagerank = graph.compute.pagerank(person)
    response = select(person.name, pagerank)

print(response.results)
# Output:
#     name         v
# 0  Alice  0.397402
# 1    Bob  0.214806
# 2  Carol  0.387792
```
