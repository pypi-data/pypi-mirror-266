# `relationalai.std`

The `relationalai.std` namespace contains the RelationalAI Query Builder Standard Library.
This includes functions for performing [aggregations](./aggregates/)
as well as classes for creating and working with [graphs](./graphs.md).

- [`alias()`](./alias.md)
- [`Vars`](./Vars.md)

## [`relationalai.std.aggregates`](./aggregates/README.md)

- [`aggregates.avg()`](./aggregates/avg.md)
- [`aggregates.count()`](./aggregates/count.md)
- [`aggregates.max()`](./aggregates/max.md)
- [`aggregates.min()`](./aggregates/min.md)
- [`aggregates.rank_asc()`](./aggregates/rank_asc.md)
- [`aggregates.rank_desc()`](./aggregates/rank_desc.md)
- [`aggregates.sum()`](./aggregates/sum.md)

## [`relationalai.std.graphs`](./graphs/README.md)

- [`graphs.Compute`](./graphs/Compute/README.md)
  - [`graphs.Compute.betweenness_centrality()`](./graphs/Compute/betweeness_centrality.md)
  - [`graphs.Compute.cosine_similarity()`](./graphs/Compute/cosine_similarity.md)
  - [`graphs.Compute.degree()`](./graphs/Compute/degree.md)
  - [`graphs.Compute.degree_centrality()`](./graphs/Compute/degree_centrality.md)
  - [`graphs.Compute.eigenvector_centrality()`](./graphs/Compute/eigenvector_centrality.md)
  - [`graphs.Compute.indegree()`](./graphs/Compute/indegree.md)
  - [`graphs.Compute.label_propagation()`](./graphs/Compute/label_propagation.md)
  - [`graphs.Compute.louvain()`](./graphs/Compute/louvain.md)
  - [`graphs.Compute.outdegree()`](./graphs/Compute/outdegree.md)
  - [`graphs.Compute.pagerank()`](./graphs/Compute/pagerank.md)
  - [`graphs.Compute.weakly_connected_component()`](./graphs/Compute/weakly_connected_component.md)
- [`graphs.Edges`](./graphs/Edges/README.md)
  - [`graphs.Edges.add()`](./graphs/Edges/add.md)
  - [`graphs.Edges.extend()`](./graphs/Edges/extend.md)
- [`graphs.Graph`](./graphs/Graph/README.md)
  - [`graphs.Graph.compute`](./graphs/Graph/compute.md)
  - [`graphs.Graph.edges`](./graphs/Graph/edges.md)
  - [`graphs.Graph.fetch()`](./graphs/Graph/fetch.md)
  - [`graphs.Graph.id`](./graphs/Graph/id.md)
  - [`graphs.Graph.model`](./graphs/Graph/model.md)
  - [`graphs.Graph.nodes`](./graphs/Graph/nodes.md)
  - [`graphs.Graph.undirected`](./graphs/Graph/undirected.md)
  - [`graphs.Graph.visualize()`](./graphs/Graph/visualize.md)
- [`graphs.Nodes`](./graphs/Nodes/README.md)
  - [`graphs.Nodes.add()`](./graphs/Nodes/add.md)
  - [`graphs.Nodes.extend()`](./graphs/Nodes/extend.md)
