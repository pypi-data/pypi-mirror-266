import relationalai as rai
from relationalai.std.graphs import Graph

model = rai.Model("weightedGraphsTest2", config=globals().get("test_config"))


def run_test(algo, ix: int, raw_edges):
    Node = model.Type(f"Node{ix}")
    graph = Graph(model, weighted=ix > 0)

    # Install graph data
    with model.rule(dynamic=True):
        for _from, _to, *weights in raw_edges:
            weight = weights[ix - 1] if ix > 0 else None
            Node.add(id=_from)
            Node.add(id=_to)
            if weight is None:
                graph.Edge.add(_from, _to)
            else:
                graph.Edge.add(_from, _to, weight=weight)

    # Test algo
    with model.query() as select:
        n = Node()
        res = select(n.id, getattr(graph.compute, algo)(n.id))

    print(res.results)

def run_tests(algo, raw_edges):
    case_count = len(raw_edges[0]) - 1
    for ix in range(0, case_count):
        run_test(algo, ix, raw_edges)

# Format (from, to, weight1, weight2, ...)

# Louvain
run_tests("louvain", [
    # First embedded 3-clique.
    (1, 2, 1.0, 0.0),
    (1, 3, 1.0, 1.0),
    (2, 3, 1.0, 0.0),

    # Second embedded 3-clique.
    (1, 4, 1.0, 1.0), (4, 5, 1.0, 10.0), (4, 6, 1.0, 1.0),

    # Connection between the embedded 3-cliques.
    (1, 4, 1.0, 1.0),

    # Weaker edges connecting the 6-clique in full.
    (1, 5, 0.2, 0.2),
    (1, 6, 0.2, 9.0),


    (2, 4, 0.2, 0.2),
    (2, 5, 0.2, 0.2),
    (2, 6, 0.2, 0.2),

    (3, 4, 0.2, 0.2),
    (3, 5, 0.2, 0.2),
    (3, 6, 0.2, 0.2)
])

# Degree
# Ensure unweighted degree still works properly on weighted graphs
run_tests("degree", [
    (11, 12, 1.0, 1.0),
    (12, 13, 1.0, -1.0),
    (13, 13, 1.0, 0.0),
    (12, 14, 1.0, 9.0)
])
