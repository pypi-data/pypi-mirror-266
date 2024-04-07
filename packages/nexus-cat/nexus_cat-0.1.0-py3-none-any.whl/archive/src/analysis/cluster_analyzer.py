from tqdm import tqdm
import numpy as np
import sys

from clstr.src.structure.cluster import Cluster


class ClusterAnalyzer:
    """
    ClusterAnalyzer class for analyzing clusters in a molecular system.

    This class provides methods to find and analyze clusters in a molecular system based on given criteria.

    Parameters:
    ----------
    - atoms (list): List of Atom objects representing the atoms in the system.
    - box (Box): Box object representing the simulation box.
    - cluster_index (int): Initial index for cluster identification.

    Attributes:
    ----------
    - atoms (list): List of Atom objects representing the atoms in the system.
    - box (Box): Box object representing the simulation box.
    - cluster_index (int): Current index for cluster identification.

    Methods:
    ----------
    - find(atom): Find the root of the cluster to which the given atom belongs.
    - union(atom1, atom2): Union two clusters to which the given atoms belong.
    - find_clusters(element, coordination1, coordination2, mask): Find clusters based on specified criteria.
    - find_alternating_clusters(element, coordination1, coordination2): Find alternating clusters based on specified criteria.
    - check_cluster_continuity(cluster): Check if a cluster is continuous.

    """

    def __init__(self, atoms, box, cluster_index, properties):
        """
        Initialize the ClusterAnalyzer.

        Parameters:
        ----------
        - atoms (list): List of Atom objects representing the atoms in the system.
        - box (Box): Box object representing the simulation box.
        - cluster_index (int): Initial index for cluster identification.
        """
        self.atoms = atoms
        self.box = box
        self.cluster_index = cluster_index
        self.properties = properties

    def find(self, atom):
        """
        Find the root of the cluster to which the given atom belongs.

        Parameters:
        ----------
        - atom (Atom): The atom for which to find the cluster root.

        Returns:
        ----------
        - Atom: The root atom of the cluster.
        """
        if atom.parent != atom:
            atom.parent = self.find(atom.parent)
        return atom.parent

    def union(self, atom1, atom2):
        """
        Union two clusters to which the given atoms belong.

        Parameters:
        ----------
        - atom1 (Atom): The first atom.
        - atom2 (Atom): The second atom.
        """
        root1 = self.find(atom1)
        root2 = self.find(atom2)
        if root1 != root2:
            root2.parent = root1

    def find_clusters(self, connectivity, neighboring_mode, coordination1, coordination2, mask):
        """
        Find clusters based on specified criteria.

        Parameters:
        ----------
        - connectivity (list of str): The connectivity type for which to find clusters.
        - coordination1 (int): The first coordination number.
        - coordination2 (int): The second coordination number.
        - mask (bool): Mask for additional criteria.

        Returns:
        ----------
        - tuple: Tuple containing lists of clusters, Cluster objects, and the number of bonded polyhedra.
        """
        
        self.cluster_index += 1
        if neighboring_mode == "bond": #expect 3 atoms in the list
            main_atom = connectivity[0]
            second_atom = connectivity[1]
            third_atom = connectivity[2]
            
        if neighboring_mode == "distance": #expect 2 atoms in the list
            main_atom = connectivity[0]
            second_atom = connectivity[1]
        
        
        element_atoms = [ atom for atom in self.atoms if atom.element == main_atom and atom.coordination == coordination1 ]

        number_of_bonded_polyhedra = 0

        for atom in tqdm(element_atoms,desc=f"Findings clusters {coordination1}-{coordination2}-...",colour="BLUE",leave=False,):
            if neighboring_mode == 'bond':
                for first_neighbor in atom.neighbors:
                    for second_neighbor in first_neighbor.neighbors:
                        if second_neighbor.coordination == coordination2 == atom.coordination:
                            self.union(atom, second_neighbor)
            
            if neighboring_mode == 'distance':
                for first_neighbor in atom.neighbors:
                    if first_neighbor.coordination == coordination2 == atom.coordination:
                        self.union(atom, first_neighbor)
            
            elif neighboring_mode!='bond' and neighboring_mode!='distance':
                raise ValueError('   Error: neighboring_value not recognized. Please verify the json configuration file.')
                sys.exit()

        clusters = {}
        for atom in tqdm(element_atoms, desc=f"Saving clusters {coordination1}-{coordination2}-...", colour="BLUE", leave=False):
            root = self.find(atom)
            clusters.setdefault(root.id, []).append(atom)

        list_of_Cluster = {}
        counter = 1
        for cluster in clusters.values():
            this_cluster = Cluster(
                box=self.box,
                type=f"{coordination1}-{coordination2}",
                id=self.cluster_index,
                configuration=atom.configuration,
                size=len(cluster),
            )
            for atom in cluster:
                atom.set_cluster_id(coordination1, coordination2, self.cluster_index)
                this_cluster.add_atom(atom)
                root = self.find(atom)
                if len(cluster) > 1:
                    number_of_bonded_polyhedra += 1

            this_cluster.check_continuity()
            this_cluster.calculate_center_of_mass()
            this_cluster.set_all_indices()

            simulation_box = self.box.get_box_dimensions(atom.configuration)
            unwrapped_positions = root.compute_unwrapped_positions(
                self.cluster_index, simulation_box
            )
            this_cluster.set_unwrapped_positions(unwrapped_positions)

            this_cluster.calculate_gyration_radius()
            this_cluster.calculate_percolation_probability()

            list_of_Cluster[counter] = this_cluster
            counter += 1
            self.cluster_index += 1

        return list(clusters.values()), list_of_Cluster, number_of_bonded_polyhedra
    
    def find_stichovite_clusters(self, connectivity, neighboring_mode, coordination1, coordination2, mask):
        """
        Find clusters based on specified criteria.

        Parameters:
        ----------
        - connectivity (list of str): The connectivity type for which to find clusters.
        - coordination1 (int): The first coordination number.
        - coordination2 (int): The second coordination number.
        - mask (bool): Mask for additional criteria.

        Returns:
        ----------
        - tuple: Tuple containing lists of clusters, Cluster objects, and the number of bonded polyhedra.
        """
        
        self.cluster_index += 1
        if neighboring_mode == "bond": #expect 3 atoms in the list
            main_atom = connectivity[0]
            second_atom = connectivity[1]
            third_atom = connectivity[2]
            
        if neighboring_mode == "distance": #expect 2 atoms in the list
            main_atom = connectivity[0]
            second_atom = connectivity[1]
        
        
        element_atoms = [ atom for atom in self.atoms if atom.element == main_atom and atom.coordination == coordination1 and atom.number_of_edge_sharing >= 2]

        number_of_bonded_polyhedra = 0

        for atom in tqdm(element_atoms,desc=f"Findings clusters {coordination1}-{coordination2}-...",colour="BLUE",leave=False,):
            if neighboring_mode == 'bond':
                for first_neighbor in atom.neighbors:
                    for second_neighbor in first_neighbor.neighbors:
                        if second_neighbor.id != atom.id:
                            if second_neighbor.coordination == coordination2 == atom.coordination and second_neighbor.number_of_edge_sharing >= 2:
                                self.union(atom, second_neighbor)
            
            if neighboring_mode == 'distance':
                for first_neighbor in atom.neighbors:
                    if first_neighbor.coordination == coordination2 == atom.coordination and atom.number_of_edge_sharing >= 2:
                        self.union(atom, first_neighbor)
            
            elif neighboring_mode!='bond' and neighboring_mode!='distance':
                raise ValueError('   Error: neighboring_value not recognized. Please verify the json configuration file.')
                sys.exit()

        clusters = {}
        for atom in tqdm(element_atoms, desc=f"Saving clusters {coordination1}-{coordination2}-...", colour="BLUE", leave=False):
            root = self.find(atom)
            clusters.setdefault(root.id, []).append(atom)

        list_of_Cluster = {}
        counter = 1
        for cluster in clusters.values():
            this_cluster = Cluster(
                box=self.box,
                type=f"stichovite",
                id=self.cluster_index,
                configuration=atom.configuration,
                size=len(cluster),
            )
            for atom in cluster:
                atom.set_stichovite_cluster_id(coordination1, coordination2, self.cluster_index)
                this_cluster.add_atom(atom)
                root = self.find(atom)
                if len(cluster) > 1:
                    number_of_bonded_polyhedra += 1

            this_cluster.check_continuity()
            this_cluster.calculate_center_of_mass()
            this_cluster.set_all_indices()

            simulation_box = self.box.get_box_dimensions(atom.configuration)
            unwrapped_positions = root.compute_unwrapped_positions(self.cluster_index, simulation_box)
            this_cluster.set_unwrapped_positions(unwrapped_positions)
            
            this_cluster.calculate_gyration_radius()
            this_cluster.calculate_percolation_probability()

            list_of_Cluster[counter] = this_cluster
            counter += 1
            self.cluster_index += 1

        return list(clusters.values()), list_of_Cluster, number_of_bonded_polyhedra

    def find_alternating_clusters(self, element, coordination1, coordination2):
        """
        Find alternating clusters based on specified criteria.

        Parameters:
        ----------
        - element (str): The element type for which to find clusters.
        - coordination1 (int): The first coordination number.
        - coordination2 (int): The second coordination number.

        Returns:
        ----------
        - tuple: Tuple containing lists of clusters, Cluster objects, and the number of bonded polyhedra.
        """
        element_atoms = [
            atom
            for atom in self.atoms
            if atom.element == element and atom.coordination == coordination1
        ]

        number_of_bonded_polyhedra = 0

        for atom in tqdm(
            element_atoms,
            desc=f"Findings alternating clusters {coordination1}-{coordination2}-{coordination1}-...",
            colour="BLUE",
            leave=False,
        ):
            # for atom in tqdm(element_atoms, desc=f'Findings clusters {coordination1}-{coordination2}-...', colour='BLUE', leave=False):
            neighbors = atom.neighbors
            for first_neighbor in neighbors:
                for second_neighbor in first_neighbor.neighbors:
                    if second_neighbor.coordination == coordination2:
                        self.union(atom, second_neighbor)

        clusters = {}
        for atom in tqdm(
            element_atoms,
            desc=f"Findings alternating clusters {coordination1}-{coordination2}-{coordination1}-...",
            colour="BLUE",
            leave=False,
        ):
            root = self.find(atom)
            clusters.setdefault(root, []).append(atom)

        list_of_Cluster = {}
        counter = 1
        for cluster in clusters.values():
            this_cluster = Cluster(
                box=self.box,
                type=f"{coordination1}-{coordination2}",
                id=self.cluster_index,
                configuration=atom.configuration,
                size=len(cluster),
            )
            for atom in cluster:
                atom.set_cluster_id(coordination1, coordination2, self.cluster_index)
                this_cluster.add_atom(atom)
                root = self.find(atom)
                if len(cluster) > 1:
                    number_of_bonded_polyhedra += 1

            this_cluster.check_continuity()
            this_cluster.calculate_center_of_mass()
            this_cluster.set_all_indices()

            simulation_box = self.box.get_box_dimensions()
            unwrapped_positions = root.compute_unwrapped_positions(
                self.cluster_index, simulation_box
            )
            this_cluster.set_unwrapped_positions(unwrapped_positions)

            this_cluster.calculate_gyration_radius()
            this_cluster.calculate_percolation_probability()

            list_of_Cluster[counter] = this_cluster
            counter += 1
            self.cluster_index += 1

        return list(clusters.values()), list_of_Cluster, number_of_bonded_polyhedra

    def check_cluster_continuity(self, cluster):
        """
        Check if a cluster is continuous.

        Parameters:
        ----------
        - cluster (list): List of Atom objects representing the cluster.

        Returns:
        ----------
        - bool: True if the cluster is continuous, False otherwise.
        """
        for atom in cluster:
            for i in range(len(atom.periodicity)):
                idx = np.where(atom.periodicity[i] != 0)[0]
                if len(idx) != 0:
                    return False
        return True
