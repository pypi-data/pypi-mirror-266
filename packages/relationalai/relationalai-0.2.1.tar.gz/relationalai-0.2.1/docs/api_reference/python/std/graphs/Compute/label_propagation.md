# `relationalai.std.graphs.Compute.label_propagation()`

```python
relationalai.std.graphs.Compute.label_propagation(node: Producer) -> Expression
```

Returns an [`Expression`](../../../Expression.md) that produces integer community labels for the producer passed to `node` using the
[label propagation](https://en.wikipedia.org/wiki/Label_propagation_algorithm) algorithm.

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

# Create a graph and add all Person objects to the set of nodes
# and the Person.follows property to the set of edges.
graph = Graph(model)
graph.Node.extend(Person)
graph.Edge.extend(Person.follows)

# Compute the PageRank of each person in the graph.
with model.query() as select:
    person = Person()
    community = graph.compute.label_propagation(person)
    response = select(person.name, community)

print(response.results)
# Output:
#     name  v
# 0  Alice  3
# 1    Bob  3
# 2  Carol  3
```

## See Also

[`Compute.weakly_connected_component`](./weakly_connected_component.md)
