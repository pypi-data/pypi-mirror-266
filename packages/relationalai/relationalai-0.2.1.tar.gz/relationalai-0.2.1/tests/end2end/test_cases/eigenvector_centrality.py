import relationalai as rai
from relationalai.std.graphs import Graph


# Test case taken from:
# https://github.com/RelationalAI/raicode/blob/8da410b949e8c47913a6faf4809234928fd8c238/test/RelLibraries/GraphAnalytics/centrality_tests.jl#L495

model = rai.Model("eigenvectorCentralityTest2", config=globals()["test_config"])
Node = model.Type("Node")

edge_list = [(1, 2), (2, 3), (3, 4)]
with model.rule(dynamic=True):
    for (x, y) in edge_list:
        node1 = Node.add(id=x)
        node2 = Node.add(id=y)
        node1.set(adjacent_to=node2)

graph = Graph(model, undirected=True)
graph.Edge.extend(Node.adjacent_to)

with model.query() as select:
    node = Node()
    centrality = graph.compute.eigenvector_centrality(node)
    response = select(node.id, centrality)