from collections import defaultdict
from copy import deepcopy
from typing import Any
from .. import dsl, errors
import gravis as gv
from . import rel, Vars

#--------------------------------------------------
# Errors
#--------------------------------------------------

def invalid_param(param:str, message:str):
    source = errors.Errors.call_source(4)
    marked = errors.mark_source(source, source.line, source.line) if source else ""
    content = f"""
    The [yellow]{param}[/yellow] parameter {message}

    {marked}
    """
    errors.print_source_error(source, "Invalid algorithm parameter", content)
    exit(1)

#--------------------------------------------------
# Validation
#--------------------------------------------------

def between(param:str, value, min, max):
    if value < min or value > max:
        invalid_param(param, f"must be between {min} and {max}")

def positive(param:str, value):
    if value <= 0:
        invalid_param(param, "must be positive")

#--------------------------------------------------
# Algos
#--------------------------------------------------

class Compute:
    def __init__(self, graph:'Graph'):
        self._graph = graph
        self._lib = dsl.global_ns.graphlib
        self._module_lib = rel.rel.graph
        self._old_lib = getattr(rel, self._graph._lib_ref())

    def _config(self, **kwargs):
        return dsl.InlineRelation(self._graph.model, [
            *[(dsl.Symbol(k), v) for k, v in kwargs.items()],
        ])

    # --------------------------------------------------
    # Degree
    # --------------------------------------------------

    # TODO: these are still in the old style graph lib
    def degree(self, node, weight=None):
        if not weight:
            return self._old_lib.degree(node)
        return self._old_lib.weighted_degree(node)

    def indegree(self, node):
        return self._lib.indegree(self._graph, node)

    def outdegree(self, node):
        return self._lib.outdegree(self._graph, node)

    # --------------------------------------------------
    # Similarity
    # --------------------------------------------------

    def cosine_similarity(self, node1, node2):
        if not self._graph.undirected:
            invalid_param("graph", "must be undirected")
        return self._module_lib.similarity.cosine_similarity(self._graph, node1, node2)

    def jaccard_similarity(self, node1, node2):
        return self._module_lib.similarity.jaccard_similarity(self._graph, node1, node2)

    # --------------------------------------------------
    # Centrality
    # --------------------------------------------------

    def pagerank(self, node, damping_factor=0.85, tolerance=1e-6, max_iter=20):
        between("damping_factor", damping_factor, 0, 1)
        positive("tolerance", tolerance)
        positive("max_iter", max_iter)

        config = self._config(
            graph=self._graph,
            damping_factor=damping_factor,
            tolerance=tolerance,
            max_iter=max_iter,
        )
        return self._lib.pagerank(config, node)

    # TODO: these are still in the old style graph lib
    def betweenness_centrality(self, node):
        return self._old_lib.betweenness_centrality(node)

    def degree_centrality(self, node):
        return self._old_lib.degree_centrality(node)

    def eigenvector_centrality(self, node):
        if not self._graph.undirected:
            invalid_param("graph", "must be undirected")
        return self._old_lib.eigenvector_centrality(node)

    # --------------------------------------------------
    # Community Detection
    # --------------------------------------------------

    def label_propagation(self, node):
        return self._old_lib.label_propagation(node)

    def weakly_connected_component(self, node):
        return self._old_lib.weakly_connected_component(node)

    def triangle_community(self, node):
        return self._old_lib.triangle_community(node)

    def infomap(self, node):
        config = self._config(graph=self._graph)
        return self._lib.infomap(config, node)

    def louvain(self, node):
        config = self._config(graph=self._graph)
        return self._lib.louvain(config, node)

#--------------------------------------------------
# Edge
#--------------------------------------------------

class EdgeInstance:
    def __init__(self, edge:'Edge', from_:Any, to:Any, kwargs:dict={}):
        self._edge = edge
        self._graph = edge._graph
        self.from_ = from_
        self.to = to
        for k, v in kwargs.items():
            self._edge._prop(k)(from_, to, v)

    def __getattr__(self, name:str):
        v = Vars(1)
        self._edge._prop(name)(self.from_, self.to, v)
        return v

    def set(self, **kwargs):
        for k, v in kwargs.items():
            self._edge._prop(k).add(self.from_, self.to, v)

    def _to_var(self):
        raise Exception("Edges can't be returned directly, you can return the from_ and to properties individually")

class Edge:
    def __init__(self, graph:'Graph'):
        self._graph = graph
        self._type = dsl.RawRelation(self._graph.model, f"graph{self._graph.id}_edges", 2)
        self._props = {}

    def _prop(self, name:str):
        if name not in self._props:
            self._props[name] = dsl.RawRelation(self._graph.model, f"graph{self._graph.id}_edge_{name}", 3)
        return self._props[name]

    def _is_weighted(self):
        return "weight" in self._props

    def extend(self, prop:'dsl.Property', **kwargs):
        type = prop._provider
        with self._graph.model.rule():
            t = type()
            self.add(t, getattr(t, prop._name), **kwargs)

    def add(self, from_:Any, to:Any, **kwargs):
        self._type.add(from_, to)
        for k, v in kwargs.items():
            self._prop(k).add(from_, to, v)
        return EdgeInstance(self, from_, to, {})

    def __call__(self, from_:Any=None, to:Any=None, **kwargs):
        if from_ is None:
            from_ = Vars(1)
        if to is None:
            to = Vars(1)
        self._type(from_, to)
        return EdgeInstance(self, from_, to, kwargs)

    def __getattribute__(self, __name: str) -> Any:
        if __name in ["add", "extend"] or __name.startswith("_"):
            return super().__getattribute__(__name)
        return self._props[__name]

#--------------------------------------------------
# Graph
#--------------------------------------------------

class Graph:
    def __init__(self, model:dsl.Graph, undirected=False, weighted=False, default_weight=1.0):
        self.model = model
        self.id = dsl.next_id()
        self.compute = Compute(self)
        self.Node = dsl.Type(model, "nodes", scope=f"graph{self.id}_")
        self.Edge = Edge(self)
        self.undirected = undirected
        self.weighted = weighted
        self.default_weight=default_weight
        self._last_fetch = None

        graph_type = "::graphlib::undirected_graph" if undirected else "::graphlib::directed_graph"
        if weighted:
            create_graph = f"""{graph_type}[{self.Edge._prop("weight")._name}]"""
        else:
            create_graph = f"{graph_type}[{self.Edge._type._name}]"

        self.model.install_raw(f"""
        bound {self.Node._type.name}
        bound {self.Edge._type._name}
        {f"bound {self.Edge._prop('weight')._name}" if weighted else ""}
        def {self._graph_ref()} = {create_graph}
        @inline
        def {self._lib_ref()} = rel:graphlib[{self._graph_ref()}]
        """)

        # Add a rule that makes all nodes used in edges are also added to
        # the nodes relation
        with model.rule():
            a, b = dsl.Vars(2)
            self.Edge._type(a, b)
            self.Node.add(a)
            self.Node.add(b)

    def _graph_ref(self):
        return f"graph{self.id}"

    def _lib_ref(self):
        return f"graphlib{self.id}"

    def _to_var(self):
        return getattr(rel, self._graph_ref())._to_var()

    def _is_weighted(self):
        return self.weighted
        # return self.edges._is_weighted()

    #--------------------------------------------------
    # Fetch
    #--------------------------------------------------

    def fetch(self):
        code = []
        code.append(f"def output:nodes(n) = {self.Node._type.name}(n)")
        for prop in self.Node._type.properties:
            code.append(f"def output:nodes:{prop.name.split('_')[-1]}(n, v) = {prop.name}(n, v)")
        code.append(f"def output:edges(a,b) = {self.Edge._type._name}(a,b)")
        for name, prop in self.Edge._props.items():
            code.append(f"def output:edges:{name}(a,b,v) = {prop._name}(a,b,v)")

        output = {"nodes": defaultdict(dict), "edges": defaultdict(dict)}
        results = self.model.exec_raw("\n".join(code), raw_results=True)
        for set_ in results.results:
            path = [v[1:] for v in set_["relationId"].split("/")[2:] if v[0] == ":"]
            if path[0] not in ["nodes", "edges"]:
                continue
            cur = output[path[0]]
            if path[0] == "nodes":
                if len(path) == 1:
                    for (n,) in set_["table"].itertuples(index=False):
                        cur[n]
                else:
                    for (n, v) in set_["table"].itertuples(index=False):
                        cur[n][path[1]] = v
            elif path[0] == "edges":
                if len(path) == 1:
                    for (a, b) in set_["table"].itertuples(index=False):
                        # If the graph is undirected, normalize the order of
                        # the source and target nodes.
                        if self.undirected and a > b:
                            a, b = b, a
                        cur[(a, b)]
                else:
                    for (a, b, v) in set_["table"].itertuples(index=False):
                        if self.undirected and a > b:
                            a, b = b, a
                        cur[(a, b)][path[1]] = v
            else:
                raise Exception(f"Unexpected path: {path}")
        self._last_fetch = output
        return output

    #--------------------------------------------------
    # Visualize
    #--------------------------------------------------

    default_visual_props = {
        "node": {
            "color": "black",
            "opacity": 1,
            "size": 10,
            "shape": "circle",
            "border_color": "black",
            "border_size": 1,
            "label_color": "black",
            "label_size": 10,
        },
        "edge": {
            "color": "#999",
            "opacity": 1,
            "size": 2,
            "shape": "circle",
            "border_color": "#999",
            "border_size": 1,
            "label_color": "black",
            "label_size": 10,
            "arrow_size": 4,
            "arrow_color": "#999",
        }
    }

    _style_map = {
        "arrow_size": "arrow_size",
        "arrow_color": "arrow_color",
    }

    def _visual_props(self, prop_def, metadata):
        for k, v in prop_def.items():
            if callable(v):
                metadata[k] = v(metadata)
        return metadata

    def _visual_dict(self, style: dict, use_cache = False) -> dict:
        data = self._last_fetch if use_cache else None
        if not data:
            data = self.fetch()
        style = deepcopy(style)
        if "node" not in style:
            style["node"] = {}
        if "edge" not in style:
            style["edge"] = {}
        merged_style = deepcopy(self.default_visual_props)
        for category in ["node", "edge"]:
            for k, v in style.get(category, {}).items():
                if not callable(v):
                    merged_style[category][k] = v
        flat_style = {
            self._style_map.get(k, f"{type}_{k}"): v
            for type, category in merged_style.items()
            for k, v in category.items()
        }

        return {
            "graph": {
                "directed": not self.undirected,
                "metadata": flat_style,
                "nodes": {
                    node_id: {
                        **({"label": info["label"]} if "label" in info else {}),
                        "metadata": self._visual_props(style["node"], info),
                    }
                    for (node_id, info) in data["nodes"].items()
                },
                "edges": [
                    {"source": source, "target": target, "metadata": self._visual_props(style["edge"], info)}
                    for ((source, target), info) in data["edges"].items()
                ],
            }
        }

    def visualize(self, three=False, style: dict | None = None, use_cache = False, **kwargs):
        style = style if style is not None else {"node": {}, "edge": {}}
        vis = gv.vis if not three else gv.three
        graph_dict = self._visual_dict(style=style, use_cache=use_cache)
        # Use defaults for the following kwargs if not provided
        new_kwargs = {
            "node_label_data_source": "label",
            "edge_label_data_source": "label",
            "edge_curvature": 0.4,
        } | kwargs
        fig = vis(graph_dict, **new_kwargs)
        return fig

#--------------------------------------------------
# Path
#--------------------------------------------------

class Path:
    def __init__(self, *args):
        self.edges = []
        self.nodes = []
        pass

    def __getitem__(self, item):
        return self

#--------------------------------------------------
# Exports
#--------------------------------------------------

__all__ = ["Graph", "Path"]
