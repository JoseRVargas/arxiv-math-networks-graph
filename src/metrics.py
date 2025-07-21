"""
metrics.py
----------

Common metrics used in the analysis notebook.

Dependencies
~~~~~~~~~~~~
* networkx>=3.0
* python-louvain *(optional; falls back to greedy modularity if missing)*

Main public functions
~~~~~~~~~~~~~~~~~~~~~
* ``compute_strength``
* ``louvain_partition``
* ``betweenness``
* ``community_densities``
"""

from collections import defaultdict
from itertools import combinations

import networkx as nx

# ---------------------------------------------------------------------------
# 1. Weighted degree (strength) ---------------------------------------------

def compute_strength(G: nx.Graph) -> dict[str, int]:
    """Return a dict mapping each node to its weighted degree ``s_i``."""
    return {n: sum(d["weight"] for *_, d in G.edges(n, data=True)) for n in G}


# ---------------------------------------------------------------------------
# 2. Community detection -----------------------------------------------------

def louvain_partition(G: nx.Graph, *, weight: str = "weight") -> dict:
    """Compute a Louvain partition.

    Falls back to :func:`networkx.algorithms.community.greedy_modularity_communities`
    if *python-louvain* is not installed.

    Parameters
    ----------
    G : nx.Graph
        The input graph.
    weight : str, default="weight"
        Edge attribute to use as weight.

    Returns
    -------
    dict
        Mapping ``{node: community_id}``.
    """
    try:
        import community.community_louvain as cl
        return cl.best_partition(G, weight=weight, resolution=1.0)
    except (ModuleNotFoundError, ImportError):
        # Fallback: greedy modularity (Clauset–Newman–Moore)
        comms = nx.algorithms.community.greedy_modularity_communities(G, weight=weight)
        part: dict[str, int] = {}
        for cid, comm in enumerate(comms):
            for n in comm:
                part[n] = cid
        return part


# ---------------------------------------------------------------------------
# 3. Betweenness centrality --------------------------------------------------

def betweenness(G: nx.Graph, *, weight: str = "weight") -> dict[str, float]:
    """Return normalized betweenness centrality (Brandes, 2001)."""
    return nx.betweenness_centrality(G, weight=weight, normalized=True)


# ---------------------------------------------------------------------------
# 4. Intra / inter‑community densities --------------------------------------

def community_densities(
    G: nx.Graph, part: dict[str, int]
) -> tuple[list[float], list[float]]:
    """Compute unweighted intra‑ and inter‑community densities.

    Returns
    -------
    (dens_intra, dens_inter) : tuple of two lists
        * ``dens_intra``  – one density value per community.
        * ``dens_inter``  – one density value per ordered pair of communities.
    """
    # group nodes by community id
    comm_dict: dict[int, set] = defaultdict(set)
    for n, cid in part.items():
        comm_dict[cid].add(n)

    comms = list(comm_dict.values())

    # intra‑community density
    dens_intra: list[float] = []
    for comm in comms:
        sub = G.subgraph(comm)
        n = sub.number_of_nodes()
        dens_intra.append(0.0 if n <= 1 else 2 * sub.number_of_edges() / (n * (n - 1)))

    # inter‑community density
    dens_inter: list[float] = []
    for c1, c2 in combinations(comms, 2):
        edges_between = sum(1 for u in c1 for v in G[u] if v in c2)
        dens_inter.append(edges_between / (len(c1) * len(c2)))

    return dens_intra, dens_inter
