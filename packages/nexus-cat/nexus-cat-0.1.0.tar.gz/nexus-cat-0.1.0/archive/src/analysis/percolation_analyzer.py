import numpy as np


class PercolationAnalyzer:
    """
    PercolationAnalyzer class for analyzing percolation properties of clusters.

    This class provides methods to analyze percolation properties of clusters, such as size, gyration radius,
    percolation probabilities, and more.

    Parameters:
    ----------
    - clusters_list (list): List of Cluster objects representing the clusters.

    Attributes:
    ----------
    - clusters (list): List of Cluster objects representing the clusters.
    - all_types (numpy.ndarray): Array containing unique cluster types.
    - all_cluster_id (numpy.ndarray): Array containing all cluster IDs.

    Methods:
    ----------
    - get_clusters_by_type(type, configuration): Get clusters of a specific type and configuration.
    - calculate_clusters_properties(type, configuration): Calculate various percolation properties of clusters.

    """

    def __init__(self, clusters_list):
        """
        Initialize the PercolationAnalyzer.

        Parameters:
        ----------
        - clusters_list (list): List of Cluster objects representing the clusters.
        """
        self.clusters = clusters_list

        self.all_types = []
        self.all_cluster_id = []

        for cluster in clusters_list:
            self.all_types.append(cluster.type)
            self.all_cluster_id.append(cluster.id)

        self.all_cluster_id = np.array(self.all_cluster_id)
        self.all_types = np.unique(np.array(self.all_types))

    def get_clusters_by_type(self, type, configuration):
        """
        Get clusters of a specific type and configuration.

        Parameters:
        ----------
        - type (str): The type of clusters to retrieve.
        - configuration (str): The configuration of clusters to retrieve.

        Returns:
        ----------
        - list: List of Cluster objects matching the specified type and configuration.
        """
        filtered_clusters = list(
            map(
                lambda cluster: cluster,
                filter(
                    lambda cluster: hasattr(cluster, "type")
                    and cluster.type == type
                    and cluster.configuration == configuration
                    and cluster.size > 1,
                    self.clusters,
                ),
            )
        )
        return filtered_clusters

    def calculate_clusters_properties(self, type, configuration):
        """
        Calculate various percolation properties of clusters.

        Parameters:
        ----------
        - type (str): The type of clusters to analyze.
        - configuration (str): The configuration of clusters to analyze.

        Returns:
        ----------
        - list: List of calculated percolation properties.
        """
        clusters_list = self.get_clusters_by_type(type, configuration)

        if len(clusters_list) == 0:
            results = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            return results

        biggest_cluster_size = 0
        percolating_cluster_size = 0
        all_non_percolating_cluster_size = np.zeros((len(clusters_list)))
        average_gyration_radiuses = np.zeros((len(clusters_list),2))
        percolation_1D, percolation_2D, percolation_3D = 0, 0, 0

        normalization_factor = 0

        percolates = False

        for i, cluster in enumerate(clusters_list):
            if cluster.size > 1:
                if cluster.percolation_probability != "":
                    percolating_cluster_size = cluster.size
                    percolates = True
                    number_of_bonded_polyhedra = cluster.number_of_bonded_polyhedra

                    if len(cluster.percolation_probability) >= 3:
                        percolation_3D = 1
                    if len(cluster.percolation_probability) >= 2:
                        percolation_2D = 1
                    if len(cluster.percolation_probability) >= 1:
                        percolation_1D = 1
                else:
                    average_gyration_radiuses[i,0] = cluster.gyration_radius
                    average_gyration_radiuses[i,1] = cluster.size
                    all_non_percolating_cluster_size[i] = cluster.size

                    number_of_bonded_polyhedra = cluster.number_of_bonded_polyhedra

                    normalization_factor += 1

        if percolates:
            biggest_cluster_size = percolating_cluster_size
        else:
            biggest_cluster_size = np.max(all_non_percolating_cluster_size)

        number_of_clusters_per_size = np.unique(
            all_non_percolating_cluster_size, return_counts=True
        )
        number_of_clusters = np.zeros_like(all_non_percolating_cluster_size)

        for i in range(len(all_non_percolating_cluster_size)):
            for j in range(len(number_of_clusters_per_size[0])):
                if (
                    all_non_percolating_cluster_size[i]
                    == number_of_clusters_per_size[0][j]
                ):
                    number_of_clusters[i] = number_of_clusters_per_size[1][j]

        number_of_polyhedra_per_cluster = (
            all_non_percolating_cluster_size * number_of_clusters
        )
        number_of_polyhedra = np.sum(number_of_polyhedra_per_cluster)

        numerator = np.sum(
            2 * (average_gyration_radiuses[:,0]**2 * all_non_percolating_cluster_size**2)
        )
        denominator = np.sum(
            (number_of_clusters_per_size[0] ** 2 * number_of_clusters_per_size[1])
        )
        if denominator == 0:
            denominator = 1
        correlation_length = np.sqrt(numerator / denominator)

        average_clusters_size = 0.0
        for i in range(len(number_of_clusters_per_size[0][:])):
            numerator = (
                number_of_clusters_per_size[0][i] ** 2
                * number_of_clusters_per_size[1][i]
            )
            denominator = np.sum(
                number_of_clusters_per_size[0] * number_of_clusters_per_size[1]
            )
            if denominator == 0:
                denominator = 1
            average_clusters_size += numerator / denominator
            if np.isnan(average_clusters_size):
                average_clusters_size = 0.0

        maximum_gyration_radius = np.max(average_gyration_radiuses[:,0])
        
        spanning_cluster_size = np.max(all_non_percolating_cluster_size)

        if percolates:
            order_parameter_p_infinite = (
                percolating_cluster_size / number_of_bonded_polyhedra
            )
        else:
            order_parameter_p_infinite = 0.0

        results = [
            average_clusters_size,
            correlation_length,
            maximum_gyration_radius,
            spanning_cluster_size,
            order_parameter_p_infinite,
            percolation_1D,
            percolation_2D,
            percolation_3D,
            biggest_cluster_size,
        ]

        return results
