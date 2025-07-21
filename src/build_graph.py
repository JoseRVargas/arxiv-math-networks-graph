"""
build_graph.py
--------------

Utility functions to load ``graph_data.json`` and return a ready‑to‑use
NetworkX graph object.

Basic usage
~~~~~~~~~~~

>>> from src.build_graph import load_graph
>>> G = load_graph("data/raw/graph_data.json", weight_min=1)
>>> print(G.number_of_nodes(), G.number_of_edges())
"""

from pathlib import Path
import json
import networkx as nx


def load_graph(json_path: str | Path, *, weight_min: int = 1) -> nx.Graph:
    """Load ``graph_data.json`` and return an ``nx.Graph``.

    Parameters
    ----------
    json_path : str or Path
        Path to the *graph_data.json* file.
    weight_min : int, default=1
        Edges with weight below this threshold are ignored—handy for quick
        visual filtering.

    Returns
    -------
    nx.Graph
        Undirected graph with edge attribute ``weight``.
    """
    json_path = Path(json_path)
    if not json_path.exists():
        raise FileNotFoundError(f"File not found: {json_path}")

    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    G = nx.Graph()
    G.add_nodes_from(data["nodes"])

    for edge in data["edges"]:
        w = edge["weight"]
        if w >= weight_min:
            G.add_edge(edge["source"], edge["target"], weight=w)

    return G
