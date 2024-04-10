# `relationalai.std.graphs.Compute.jaccard_similarity()`

```python
relationalai.std.graphs.Compute.jaccard_similarity(node1: Producer, node2: Producer) -> Expression
```

Returns an [`Expression`](../../../Expression.md) that produces the
[Jaccard similarity](https://en.wikipedia.org/wiki/Jaccard_index) values
between the producers passed to `node1` and `node2`.

## Supported Graph Types

| Graph Type | Supported | Notes |
| :--- | :--- | :------ |
| Directed | Yes |   |
| Undirected | Yes |   |

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `node1` | [`Producer`](../../../Producer/README.md) | A producer that produces object IDs of nodes. |
| `node2` | [`Producer`](../../../Producer/README.md) | A producer that produces object IDs of nodes. |

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
    alice.set(friend=bob)
    bob.set(friend=carol)

# Create a graph and add all `Person` objects to the set of nodes
# and the `Person.friend` property to the set of edges.
# Note that `cosine_similarity` is only defined for undirected graphs.
graph = Graph(model, undirected=True)
graph.Node.extend(Person)
graph.Edge.extend(Person.friend)

# Compute the cosine similarity between each pair of distinct people.
with model.query() as select:
    person1 = Person()
    person2 = Person()
    person1 != person2
    similarity = graph.compute.jaccard_similarity(person1, person2)
    response = select(person1.name, person2.name, similarity)

print(response.results)
# Output:
#     name  name2    v
# 0  Alice  Carol  1.0
# 1  Carol  Alice  1.0
```

> [!NOTE]
> Pairs of nodes for which the Jaccard similarity is `0.0` are excluded from results.
