# `relationalai.std.graphs.Compute.weakly_connected_component()`

```python
relationalai.std.graphs.Compute.weakly_connected_component(node: Producer) -> Expression
```

Returns an [`Expression`](../../../Expression.md) that produces the component IDs of the
[weakly connected components](https://en.wikipedia.org/wiki/Weak_component)
to which the nodes produced by the `node` producer belong.

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

An [`Expression`](../../../Expression.md) object that produces `string` values.

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

# Compute the weakly connected component for each person in the graph.
with model.query() as select:
    person = Person()
    component = graph.compute.weakly_connected_component(person)
    response = select(person.name, component)

print(response.results)
# Output:
#     name                       v
# 0  Alice  JCOgZI0tb1qNRTyXYhDFOw
# 1    Bob  JCOgZI0tb1qNRTyXYhDFOw
# 2  Carol  JCOgZI0tb1qNRTyXYhDFOw
```

Component IDs are the object IDs of the objects chosen to represent the components.
In the preceding example, all three nodes are in the same component.

## See Also

[`Compute.label_propagation`](./label_propagation.md)
