# `relationalai.std.graphs.Graph.visualize()`

```python
relationalai.std.graphs.Graph.visualize(three: bool = False, style: dict = {}, **kwargs) ->
```

Visualize a graph.

## Parameters

| Name | Type | Description |
| :--- | :--- | :------ |
| `three` | `bool` | Whether or not to use the `three.js` 3D render engine. Defaults to `False`. |
| `style` | `dict` | A dictionary with a `"nodes"` key and an `"edges"` key that defines the visual style of the graph.
| `**kwargs` | `Any` | Additional keyword arguments to pass to the gravis visualization library. See the [gravis docs](https://robert-haas.github.io/gravis-docs/index.html) for full details. |

## Returns

A gravis [`Figure`](https://robert-haas.github.io/gravis-docs/rst/api/figure.html) object.

## Example

```python
import relationalai as rai
from relationalai.std.graphs import Graph

# Create a model with a `Person` type.
model = rai.Model("socialNetwork")
Person = model.Type("Person")

# Add some people to the model and connect them with a `follows` property.
with model.rule():
    alice = Person.add(name="Alice")
    bob = Person.add(name="Bob")
    alice.set(follows=bob)

# Create a graph with edges from the `Person.follows` property.
graph = Graph(model)
graph.Node.extend(Person)
graph.Edge.extend(Person.follows)

# Visualize the graph.
fig = graph.visualize()
fig.display()
```

The figure opens in a new web browser window.

![A graph with two nodes and one edge.](./img/graph-viz.png)

> [!TIP]
> In a Jupyter Notebook, `graph.visualize()` will display the figure.
> You do not need to assign the figure to a variable and call the `.display()` method.

You may change the label, color, and size of nodes and edges:

```python
import relationalai as rai
from relationalai.std.graphs import Graph

# Create a model with a `Person` type.
model = rai.Model("socialNetwork")
Person = model.Type("Person")
Brand = model.Type("Brand")

# Add some people to the model and connect them with a `follows` property.
with model.rule():
    alice = Person.add(name="Alice")
    bob = Person.add(name="Bob")
    acme = Brand.add(name="Acme")
    alice.set(follows=bob).set(follows=acme)
    bob.set(follows=acme)

# Create a graph with edges from the `Person.follows` property.
graph = Graph(model)
graph.Node.extend(Person, label=Person.name, color="blue")
graph.Node.extend(Brand, label=Brand.name, color="red")
graph.Edge.extend(Person.follows)

# Compute the PageRank of people in the graph and use it for the node's size.
with model.rule():
    person = Person()
    rank = graph.compute.pagerank(person)
    graph.Node.add(person, size=rank * 50)

fig = graph.visualize()
fig.display()
```

![A graph with two blue nodes labeled "Bob" and "Alice" and one red node labeled "Acme." The "Bob" node is larger than the "Alice" node.](./img/graph-viz-with-labels-and-colors.png)

You can also describe the visual properties of nodes and edges by passing a dictionary to the `style` parameter.
The following example produces the same visualization as the preceding example:

```python
import relationalai as rai
from relationalai.std.graphs import Graph

# Create a model with a `Person` type.
model = rai.Model("socialNetwork")
Person = model.Type("Person")
Brand = model.Type("Brand")

# Add some people to the model and connect them with a `follows` property.
with model.rule():
    alice = Person.add(name="Alice")
    bob = Person.add(name="Bob")
    acme = Brand.add(name="Acme")
    alice.set(follows=bob).set(follows=acme)
    bob.set(follows=acme)

# Create a graph with edges from the `Person.follows` property.
graph = Graph(model)
graph.Node.extend(Person, kind="person")
graph.Node.extend(Brand, kind="brand")
graph.Edge.extend(Person.follows)

# Compute the PageRank of people in the graph and use it for the node's size.
with model.rule():
    person = Person()
    rank = graph.compute.pagerank(person)
    graph.Node.add(person)

graph.visualize(style={
    "nodes": {
        "color": lambda n: {"person": "blue", "brand": "red"}.get(n["kind"]),
        "size": lambda n: n.get("rank", 1.0) * 50,
    },
    "edges": {}
})
```

## See Also

[`Graph.visualize()`](./visualize.md)
