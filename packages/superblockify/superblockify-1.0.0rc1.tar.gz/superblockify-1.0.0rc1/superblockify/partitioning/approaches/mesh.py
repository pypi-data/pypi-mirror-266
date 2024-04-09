"""Random net partitioning approach"""

from numpy.random import default_rng

from .attribute import AttributePartitioner


class MeshPartitioner(AttributePartitioner):
    """Partitioner that spans a mesh of random POIs through the network.

    Connections in between will be chosen based on the shortest paths.
    """

    def write_attribute(self, parameters=None, seed=None, **kwargs):
        """Set the sparsified graph to a generated mesh.

        To generate the mesh, later used as the sparsified graph, random nodes will
        be selected and connected between each other. The connections will be chosen
        based on the shortest paths between the nodes.

        Parameters
        ----------
        parameters : dict, optional
            Parameters for the mesh generation, by default None.
        seed : int, optional
            Seed for the random number generator, by default None.

        """
        rng = default_rng(seed)
        params = {}
        params.update(parameters or {})

        # 1. Calculate the shortest paths
        self.calculate_metrics_before(make_plots=kwargs.get("make_plots", False))

        # 2. Get nodes to connect
