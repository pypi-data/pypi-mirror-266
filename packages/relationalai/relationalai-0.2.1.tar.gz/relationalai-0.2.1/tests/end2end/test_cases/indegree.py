import relationalai as rai
from relationalai.std.graphs import Graph


# Test case taken from:
# https://github.com/RelationalAI/raicode/blob/8da410b949e8c47913a6faf4809234928fd8c238/test/RelLibraries/GraphAnalytics/graph_similarity_tests.jl#L238

model = rai.Model("indegreeTest2", config=globals().get("test_config"))
Node = model.Type("Node")

edge_list = [(11, 12), (12, 13), (13, 13), (13, 14)]
with model.rule(dynamic=True):
    for (x, y) in edge_list:
        node1 = Node.add(id=x)
        node2 = Node.add(id=y)
        node1.set(adjacent_to=node2)

# Undirected case
undirected_graph = Graph(model, undirected=True)
undirected_graph.Edge.extend(Node.adjacent_to)

with model.query() as select:
    node = Node()
    degree = undirected_graph.compute.indegree(node)
    response = select(node.id, degree)

# Directed case
directed_graph = Graph(model)
directed_graph.Edge.extend(Node.adjacent_to)

with model.query() as select:
    node = Node()
    degree = directed_graph.compute.indegree(node)
    response = select(node.id, degree)
