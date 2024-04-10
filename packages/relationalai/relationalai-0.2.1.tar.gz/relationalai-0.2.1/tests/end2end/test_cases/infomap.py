import relationalai as rai
from relationalai.std.graphs import Graph


# Test case taken from:
# https://github.com/RelationalAI/raicode/blob/a4b86f395ea1f4bbc0add40b3764aa17c1272110/src/rel/graphlib-infomap.rel#L37

model = rai.Model("infomapTest", config=globals()["test_config"])
Node = model.Type("Node")

edge_list = [
    (1, 2), (1, 3), (2, 3),  # The first three-clique.
    (4, 5), (4, 6), (5, 6),  # The second three-clique.
    (1, 3),  # The connection between the three-cliques.
]
with model.rule(dynamic=True):
    for (x, y) in edge_list:
        node1 = Node.add(id=x)
        node2 = Node.add(id=y)
        node1.set(adjacent_to=node2)

graph = Graph(model)
graph.Edge.extend(Node.adjacent_to)

with model.query() as select:
    node = Node()
    community = graph.compute.infomap(node)
    select(node.id, community)