# `relationalai.std.graphs.Compute.infomap()`

```python
relationalai.std.graphs.Compute.infomap(node: Producer) -> Expression
```

Returns an [`Expression`](../../../Expression.md) that produces community IDs for nodes using the
[Infomap algorithm](https://www.mapequation.org/assets/publications/EurPhysJ2010Rosvall.pdf).

## Supported Graph Types

| Graph Type | Supported | Notes |
| :--- | :--- | :------ |
| Directed | Yes |   |
| Undirected | Yes |   |
| Weighted | Yes |   |

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `node` | [`Producer`](../../../Producer/README.md) | A producer that produces node objects. |

## Returns

An [`Expression`](../../../Expression.md) object that produces `int` community IDs.

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
    dan = Person.add(name="Dan")
    edgar = Person.add(name="Edgar")
    alice.set(follows=bob)
    carol.set(follows=dan)

# Create a graph and add all `Person` objects to the set of nodes
# and the `Person.follows` property to the set of edges.
graph = Graph(model)
graph.Edge.extend(Person.follows)
graph.Node.extend(Person)  # Ensures isolated nodes like `edgar` are included.

# Detect communities of nodes using `infomap()`.
with model.query() as select:
    person = Person()
    community = graph.compute.infomap(person)
    response = select(person.name, community)

print(response.results)
# Output:
#     name  v
# 0  Alice  2
# 1    Bob  2
# 2  Carol  1
# 3    Dan  1
```

> [!NOTE]
> Isolated nodes are not assigned community IDs and are excluded from the results.
