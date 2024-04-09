import relationalai as rai
from relationalai.std.graphs import Graph


# Test case taken from:
# https://github.com/RelationalAI/raicode/blob/8da410b949e8c47913a6faf4809234928fd8c238/test/RelLibraries/GraphAnalytics/graph_community_detection_louvain_tests.jl#L17
# Note that the expected output here differs from the expected output in the Rel test.
# This is because the Rel uses the integer IDs for the node IDs in the graph,
# while PyRel uses the hash as the node ID.

model = rai.Model("louvainTest2", config=globals().get("test_config"))
Node = model.Type("Node")

edge_list = [(10, 10), (20, 20), (30, 30), (40, 40), (50, 50)]
with model.rule(dynamic=True):
    for (x, y) in edge_list:
        node1 = Node.add(id=x)
        node2 = Node.add(id=y)
        node1.set(adjacent_to=node2)

graph = Graph(model)
graph.Edge.extend(Node.adjacent_to)

with model.query() as select:
    node = Node()
    community = graph.compute.louvain(node)
    response = select(node.id, community)