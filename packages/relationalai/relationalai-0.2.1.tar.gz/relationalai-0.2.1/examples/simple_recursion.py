import relationalai as rai

graph = rai.Model("RecursiveExample")
Edge = graph.Type("Edge")

## Find all paths reachable from a given start node and an initial set of 1-hop edges.

with graph.rule():
    # Create some initial edges
    Edge.add(start=1, finish=2)
    Edge.add(start=2, finish=3)
    Edge.add(start=3, finish=5)
    Edge.add(start=4, finish=6)
    # Expecting 1 -> 2 -> 3 -> 5, 4 -> 6

with graph.rule():
    first = Edge()
    second = Edge(start = first.finish)
    Edge.add(start=first.start, finish=second.finish)

with graph.query() as select:
    edge = Edge()
    response = select(edge, edge.start, edge.finish)

print(response)
