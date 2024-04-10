# `relationalai.std.graphs.Graph.fetch()`

```python
relationalai.std.graphs.Graph.fetch() ->
```

Returns a dictionary with two keys, `"nodes"` and `"edges"`, that represents the entire graph.

## Parameters

None

## Returns

A `dict` object.

## Example

```python
from pprint import pprint

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
graph.Node.extend(Person, label=Person.name)
graph.Edge.extend(Person.follows)

# Fetch the graph.
pprint(graph.fetch())
# Output:
# {'edges': defaultdict(<class 'dict'>,
#                       {('JCOgZI0tb1qNRTyXYhDFOw', 'v3PMBEmnWi5E2MxI4bGfzQ'): {}}),
#  'nodes': defaultdict(<class 'dict'>,
#                       {'JCOgZI0tb1qNRTyXYhDFOw': {'label': 'Alice'},
#                        'v3PMBEmnWi5E2MxI4bGfzQ': {'label': 'Bob'}})}
```

## See Also

[`Graph.visualize()`](./visualize.md)
