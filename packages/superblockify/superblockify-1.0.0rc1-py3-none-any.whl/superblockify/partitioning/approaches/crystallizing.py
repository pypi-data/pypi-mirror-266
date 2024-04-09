"""Crystalling partitioner."""

from networkx import set_edge_attributes
from numpy import sum as npsum
from numpy.random import default_rng

from .attribute import AttributePartitioner
from ..representative import find_representative_node_id
from ...config import logger


class CrystallizingPartitioner(AttributePartitioner):
    """Partitioner that crystallizes the sparsified network randomly.

    Starts at nucleus node, like a crystal and grows outwards with some rules.
    """

    def write_attribute(
        self, parameters=None, fraction=0.3, seed=None, bc_type="normal", **kwargs
    ):
        """Set the sparsified graph to a crystallized network.

        The new nodes have certain fractions of being selected randomly:
            - rand_adj: random adjacent node
            - rand: random reachable node
            - l_bc: reachable node with the lowest betweenness centrality
            - h_bc: reachable node with the highest betweenness centrality
            - l_w: reachable edge with the lowest weight (length, travel_time, ...)
            - h_w: reachable edge with the highest weight
            - l_deg: reachable node with the lowest degree
            - h_deg: reachable node with the highest degree
            - h_dist: reachable node with the greatest distance to the included nodes

        Additionally, there are multiplicative factors for the probabilities:
            - rev: node has an edge in the opposite direction

        If there are multiple nodes with the same value, one is selected randomly.

        Parameters
        ----------
        parameters : dict, optional
            Parameters for the crystallization, by default None.
            If None, the default parameters are used:
            {`rand_adj`: 2, `rand`: 0, `l_bc`: 1, `h_bc`: 1, `l_w`: 0.5, `h_w`: 1,
            `l_deg`: 0.5, `h_deg`: 0.5, `h_dist`: 1, `rev`: 2}
        fraction : float, optional
            Terminating condition for the crystallization, by default 0.3.
            Fraction of nodes that are included in the crystal.
        seed : int, optional
            Seed for the random number generator, by default None.
        bc_type : str, optional
            Type of betweenness centrality to use, by default `normal`.
            It Can be `normal`, `length`, or `linear`.
            Read more about the centrality types in the resources of
            :func:`superblockify.metrics.measures.betweenness_centrality`.
        """
        rng = default_rng(seed)
        params = {
            "rand_adj": 2,
            "rand": 0,
            "l_bc": 1,
            "h_bc": 1,
            "l_w": 0.5,
            "h_w": 1,
            "l_deg": 0.5,
            "h_deg": 0.5,
            "h_dist": 1,
            "rev": 2,
        }
        params.update(parameters or {})
        # normalize probabilities
        params = {k: v / npsum(list(params.values())) for k, v in params.items()}

        # initialize attribute
        self.attribute_label = "crystallized"
        set_edge_attributes(self.graph, values=0, name=self.attribute_label)
        # if betweennesses might be used, prepare them
        if params["l_bc"] > 0 or params["h_bc"] > 0:
            self.calculate_metrics_before(make_plots=kwargs.get("make_plots", False))

        # start with central node
        nucleus = find_representative_node_id(self.graph)
        # crystal
        crystal = self.graph.subgraph([nucleus])
        # reachable nodes - adjacent nodes without included nodes
        reachable = set(self.graph.adj[nucleus]) - set(crystal.nodes)
        # remaining nodes - all nodes without included nodes
        remaining = set(self.graph.nodes) - set(crystal.nodes)
        # add until fraction of nodes is reached
        while len(crystal) / len(self.graph) < fraction:
            # random choice of criteria
            criteria = rng.choice(list(params.keys()), p=list(params.values()))
            # random choice of node
            if criteria == "rand":
                node = rng.choice(list(remaining))
            elif criteria == "rand_adj":
                node = rng.choice(list(reachable))
            # node with the lowest betweenness
            elif criteria == "l_bc":
                node = min(
                    reachable,
                    key=lambda x: self.graph.nodes[x][f"node_betweenness_{bc_type}"],
                )
            # node with the highest betweenness
            elif criteria == "h_bc":
                node = max(
                    reachable,
                    key=lambda x: self.graph.nodes[x][f"node_betweenness_{bc_type}"],
                )
            # edge with the lowest weight
            elif criteria == "l_w":
                edge = min(
                    reachable,
                    key=lambda x: self.graph.edges[x]["length"],
                )
                node = edge[1]
