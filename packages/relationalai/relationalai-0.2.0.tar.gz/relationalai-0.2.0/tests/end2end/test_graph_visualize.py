import random
import pytest
import relationalai as rai
from relationalai.std.graphs import Graph

DEFAULT_METADATA = {
    'arrow_color': '#999',
    'arrow_size': 4,
    'edge_border_color': '#999',
    'edge_border_size': 1,
    'edge_color': '#999',
    'edge_label_color': 'black',
    'edge_label_size': 10,
    'edge_opacity': 1,
    'edge_shape': 'circle',
    'edge_size': 2,
    'node_border_color': 'black',
    'node_border_size': 1,
    'node_color': 'black',
    'node_label_color': 'black',
    'node_label_size': 10,
    'node_opacity': 1,
    'node_shape': 'circle',
    'node_size': 10,
}


def make_graph(model, test_input: dict):
    Node = model.Type("Node")

     # Add objects to the model.
    with model.rule(dynamic=True):
        for (id1, adj) in test_input["adj_list"].items():
            node1 = Node.add(id=id1)
            for id2 in adj:
                node2 = Node.add(id=id2)
                node1.set(adjacent_to=node2)

    # Create a graph object.
    graph = Graph(model, undirected=test_input["undirected"])

    # Add nodes to the graph.
    with model.rule(dynamic=True):
        for (id, props) in test_input["node_props"].items():
            node = Node(id=id)
            graph.Node.add(node, **props)

    # Add edges to the graph.
    with model.rule(dynamic=True):
        for ((id1, id2), props) in test_input["edge_props"].items():
            node1, node2 = Node(id=id1), Node(id=id2)
            graph.Edge.add(node1, node2, **props)

    return graph

# @NOTE: This should replaced with the globals lookup from
# https://github.com/RelationalAI/relationalai-python/pull/117 once that drops.
def unique_model_name(name: str):
    random_number = random.randint(1000000000, 9999999999)
    return f"{name}_{random_number}"

# Test that graph._visual_dict() returns a dictionary with the correct keys and values
@pytest.mark.parametrize(
    ["test_input", "expected_dict"],
    [
        # Undirected graph with one data edge, no props, default style
        pytest.param(
            {
                "adj_list": {1: [2]},
                "node_props": {1: {}, 2: {}},
                "edge_props": {(1, 2): {}},
                "undirected": True,
                "style": {},
                "kwargs": {},
            },
            {
                'directed': False,
                'nodes': {
                    'jLWfdS5w49/Nqwx+mYthYw': {'metadata': {}},
                    'peH/vEX2TeRy3NL41/2Nag': {'metadata': {}},
                },
                'edges': [{'metadata': {}, 'source': 'jLWfdS5w49/Nqwx+mYthYw', 'target': 'peH/vEX2TeRy3NL41/2Nag'}],
                'metadata': DEFAULT_METADATA,
            },
            id="undirected_no_props_default_style",
        ),
        # Directed graph with one data edge, no props, no style
        pytest.param(
            {
                "adj_list": {1: [2]},
                "node_props": {1: {}, 2: {}},
                "edge_props": {(1, 2): {}},
                "undirected": False,
                "style": {},
                "kwargs": {},
            },
            {
                'directed': True,
                'nodes': {
                    'jLWfdS5w49/Nqwx+mYthYw': {'metadata': {}},
                    'peH/vEX2TeRy3NL41/2Nag': {'metadata': {}},
                },
                'edges': [
                    {'metadata': {}, 'source': 'peH/vEX2TeRy3NL41/2Nag', 'target': 'jLWfdS5w49/Nqwx+mYthYw'},
                ],
                'metadata': DEFAULT_METADATA,
            },
            id="directed_no_props_default_style",
        ),
        # Undirected graph with two data edges (but one graph edge), props, custom node and edge colors.
        # Shows property merge behavior for undirected graphs with multiple data edges for a single graph edge.
        # Compare to the directed graph case below.
        pytest.param(
            {
                "adj_list": {1: [2]},
                "node_props": {1: {'color': 'blue'}, 2: {'color': 'red'}},
                "edge_props": {
                    (1, 2): {'color': 'green'},
                    (2, 1): {'color': 'yellow'}
                },
                "undirected": True,
                "style": {
                    'nodes': {'color': lambda n: n['color']},
                    'edges': {'color': lambda e: e['color']}
                },
                "kwargs": {},
            },
            {
                'directed': False,
                'nodes': {
                    'jLWfdS5w49/Nqwx+mYthYw': {'metadata': {'color': 'red'}},
                    'peH/vEX2TeRy3NL41/2Nag': {'metadata': {'color': 'blue'}},
                },
                'edges': [{'metadata': {'color': 'green'}, 'source': 'jLWfdS5w49/Nqwx+mYthYw', 'target': 'peH/vEX2TeRy3NL41/2Nag'}],
                'metadata': DEFAULT_METADATA,
            },
            id="undirected_with_props_custom_style",
        ),
        # Directed graph with two data edges (and two graph edges), props, custom node and edge colors.
        pytest.param(
            {
                "adj_list": {1: [2]},
                "node_props": {1: {'color': 'blue'}, 2: {'color': 'red'}},
                "edge_props": {
                    (1, 2): {'color': 'green'},
                    (2, 1): {'color': 'yellow'}
                },
                "undirected": False,
                "style": {
                    'nodes': {'color': lambda n: n['color']},
                    'edges': {'color': lambda e: e['color']}
                },
                "kwargs": {},
            },
            {
                'directed': True,
                'nodes': {
                    'jLWfdS5w49/Nqwx+mYthYw': {'metadata': {'color': 'red'}},
                    'peH/vEX2TeRy3NL41/2Nag': {'metadata': {'color': 'blue'}},
                },
                'edges': [
                    {'metadata': {'color': 'yellow'}, 'source': 'jLWfdS5w49/Nqwx+mYthYw', 'target': 'peH/vEX2TeRy3NL41/2Nag'},
                    {'metadata': {'color': 'green'}, 'source': 'peH/vEX2TeRy3NL41/2Nag', 'target': 'jLWfdS5w49/Nqwx+mYthYw'}
                ],
                'metadata': DEFAULT_METADATA,
            },
            id="directed_with_props_custom_style",
        ),
    ],
)
def test_visual_dict(engine_config, test_input, expected_dict):
    model_name = unique_model_name("testGraphVisualDict")
    model = rai.Model(model_name, config=engine_config)
    graph = make_graph(model, test_input)
    visual_dict = graph._visual_dict(style=test_input["style"])
    assert visual_dict == {'graph': expected_dict}

# Test that graph.visualize() returns a value and does not raise an exception.
@pytest.mark.parametrize(
        ["test_input"],
        [
            pytest.param(
                {
                    "adj_list": {1: [2]},
                    "node_props": {1: {}, 2: {}},
                    "edge_props": {(1, 2): {}},
                    "undirected": True,
                    "style": {},
                    "kwargs": {},
                },
                id="no_style_no_kwargs",
            ),
            pytest.param(
                {
                    "adj_list": {1: [2]},
                    "node_props": {1: {"id": "node1"}, 2: {"id": "node2"}},
                    "edge_props": {(1, 2): {"id": "edge1"}},
                    "undirected": True,
                    "style": {},
                    "kwargs": {
                        "edge_label_data_source": "id",
                        "node_label_data_source": "id",
                        "edge_curvature": 1.0,
                    },
                },
                id="no_style_override_kwargs",
            ),
        ]
)
def test_visualize(engine_config, test_input):
    model_name = unique_model_name("testGraphVisualize")
    model = rai.Model(model_name, config=engine_config)
    graph = make_graph(model, test_input)
    assert graph.visualize(style=test_input["style"], **test_input["kwargs"]) is not None
