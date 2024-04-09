import relationalai as rai
from relationalai.std.graphs import Graph


# Test case taken from:
# https://github.com/RelationalAI/raicode/blob/8da410b949e8c47913a6faf4809234928fd8c238/test/RelLibraries/GraphAnalytics/graph_similarity_tests.jl#L238

model = rai.Model("cosineSimilarityTest2", config=globals().get("test_config"))
Node = model.Type("Node")

edge_list = [(11, 12), (12, 13), (13, 13), (12, 14), (14, 13)]
with model.rule(dynamic=True):
    for (x, y) in edge_list:
        node1 = Node.add(id=x)
        node2 = Node.add(id=y)
        node1.set(adjacent_to=node2)

graph = Graph(model, undirected=True)
graph.Edge.extend(Node.adjacent_to)

with model.query() as select:
    node1 = Node(id=12)
    node2 = Node(id=14)
    similarity = graph.compute.cosine_similarity(node1, node2)
    response = select(node1.id, node2.id, similarity)