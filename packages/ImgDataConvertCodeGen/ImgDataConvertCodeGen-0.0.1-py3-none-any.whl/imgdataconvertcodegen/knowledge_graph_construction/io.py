import json
import networkx as nx


def save_graph(graph, save_path):
    data = json.dumps(graph, default=nx.node_link_data)
    with open(save_path, 'w') as f:
        f.write(data)


def load_graph(path):
    with open(path, 'r') as f:
        data = json.load(f)
    graph = nx.node_link_graph(data)
    return graph
