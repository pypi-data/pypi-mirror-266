# `relationalai.std.graphs.Edges.add()`

```python
relationalai.std.graph.Edge.add(from_: Producer, to: Producer, **kwargs: Any) -> None
```

Adds edges to the graph from objects produced by the `from_` producer to objects produced by the `to` Producer.
Edge properties may be passed as keyword arguments to `**kwargs`.
You can use and display these properties in graph visualizations.
Objects produced by the `from_` and `to` producers are automatically added to the graph's nodes.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `from_` | [`Producer`](../../../Producer/README.md) | A producer that produces the initial nodes of edges. |
| `to` | [`Producer`](../../../Producer/README.md) | A producer that produces the terminal nodes of edges. |
| `**kwargs` | `Any` | Keyword arguments representing property name and value pairs. Values may be literals or `Producer` objects. |

## Returns

`None`.

## Example

```python
import relationalai as rai
from relationalai.std.graphs import Graph

# Create a model with `Person` and `Transaction` types.
model = rai.Model("transactions")
Person = model.Type("Person")
Transaction = model.Type("Transaction")

# Add some people and transactions to the model.
with model.rule():
    alice = Person.add(name="Alice")
    bob = Person.add(name="Bob")
    Transaction.add(sender=bob, receiver=alice, amount=100.0)

# Create a graph.
graph = Graph(model)
graph.Node.extend(Person)

# Add transactions to the graph as edges.
with model.rule():
    transaction = Transaction()
    graph.Edge.add(
        from_=transaction.sender,
        to=transaction.receiver,
        weight=transaction.amount
    )
```

## See Also

[`Edges.extend()`](./extend.md) and [`Graph.edges`](../Graph/edges.md).
