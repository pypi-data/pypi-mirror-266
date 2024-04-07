import numpy as np
from clstr.src.data import (
    chemical_symbols,
    correlation_lengths,
    atomic_numbers,
    atomic_masses,
)
from tqdm import tqdm


class Atom:
    """
    Atom class representing an atom in a molecular system.

    This class provides methods to manage and retrieve information about an atom, such as its element,
    position, charge, configuration, neighbors, correlation length, atomic mass, coordination, and cluster membership.

    Parameters:
    ----------
    - element (str): Chemical symbol of the atom.
    - id (int): Unique identifier for the atom.
    - position (tuple): Spatial coordinates of the atom.
    - charge (int): Charge associated with the atom (default is 0).
    - configuration (int): Configuration index associated with the atom in the trajectory (default is 0).

    Attributes:
    ----------
    - element (str): Chemical symbol of the atom.
    - id (int): Unique identifier for the atom.
    - position (tuple): Spatial coordinates of the atom.
    - charge (int): Charge associated with the atom.
    - configuration (int): Configuration index associated with the atom in the trajectory.
    - neighbors (list): List of Atom objects representing the neighbors connected to the atom.
    - not_filtered_neighbors (list): List of Atom objects representing the neighbors connected to the atom (not filtered).
    - correlation_length (float): Correlation length associated with the atom.
    - atomic_mass (float): Atomic mass associated with the atom.
    - coordination (int): Coordination number of the atom.
    - cluster_type (list): List of cluster types to which the atom belongs.
    - cluster_id (int): Identifier of the cluster to which the atom belongs.
    - parent (Atom): Reference to the parent atom in the union-find structure.
    - unwrapped_position (tuple): Unwrapped spatial coordinates of the atom.

    Methods:
    ----------
    - update_position(new_position): Updates the position of the atom.
    - get_element(): Returns the chemical element of the atom.
    - get_id(): Returns the id of the atom.
    - get_position(): Returns the spatial coordinates of the atom.
    - get_charge(): Returns the charge associated with the atom.
    - get_configuration(): Returns the configuration index associated with the atom.
    - get_neighbors(): Returns the list of neighbors connected to the atom.
    - add_neighbor(other_atom): Adds a neighbor between this atom and another specified atom.
    - add_not_filtered_neighbor(other_atom): Adds a neighbor between this atom and another specified atom.
    - remove_neighbor(other_atom): Removes a neighbor between this atom and another specified atom.
    - get_correlation_length(): Returns the correlation length associated with the atom.
    - get_atomic_mass(): Returns the atomic mass associated with the atom.
    - calculate_coordination(): Calculates the coordination associated with the atom.
    - get_coordination(): Returns the coordination associated with the atom.
    - get_cluster_id(): Returns the id of the cluster to which the atom belongs.
    - set_cluster_id(coordination_1, coordination_2, cluster_id): Sets the id of the cluster to which the atom belongs.
    - reset_cluster_id(): Resets the cluster id of the atom.
    - compute_unwrapped_positions(cluster_index, box_size): Computes unwrapped positions for all atoms in the cluster.
    - unwrap_position(position, box_size): Unwraps position considering periodic boundary conditions.

    """

    def __init__(self, element, id, position, charge=0, configuration=0, cutoffs=[]):
        """
        Initialize the Atom.

        Parameters:
        ----------
        - element (str): Chemical symbol of the atom.
        - id (int): Unique identifier for the atom.
        - position (tuple): Spatial coordinates of the atom.
        - charge (int): Charge associated with the atom (default is 0).
        - configuration (int): Configuration index associated with the atom in the trajectory (default is 0).
        """
        self.element = element
        self.id = id
        self.position = position
        self.charge = charge
        self.configuration = configuration
        self.cutoffs = cutoffs
        self.neighbors = []
        self.not_filtered_neighbors = []
        self.periodicity = []
        self.distance_periodicity = []
        self.correlation_length = 0
        self.atomic_mass = 0
        self.coordination = 0
        self.cluster_type = []
        self.cluster_id = None
        self.parent = self
        self.unwrapped_position = position
        self.number_of_edge_sharing = 0

        if self.element in chemical_symbols:
            index = np.where(self.element == chemical_symbols)[0].astype(np.int32)
            self.correlation_length = correlation_lengths[index][0]
            self.atomic_mass = atomic_masses[index][0]
        else:
            print("Failed to create Atom object with the chemical symbol")
            return None

    def update_position(self, new_position):
        """
        Updates the position of the atom.

        Parameters
        ----------
        new_position : tuple
            The new spatial coordinates of the atom.
        """
        self.position = new_position

    def get_element(self):
        """Returns the chemical element of the atom."""
        return self.element

    def get_id(self):
        """Returns the id of the atom."""
        return self.id

    def get_position(self):
        """Returns the spatial coordinates of the atom."""
        return self.position

    def get_charge(self):
        """Returns the charge associated with the atom."""
        return self.charge

    def get_configuration(self):
        """Returns the configuration index associated with the atom in the trajectory."""
        return self.configuration

    def get_neighbors(self):
        """Returns the list of neighbors connected to the atom."""
        return self.neighbors

    def add_neighbor(self, other_atom, periodicity):
        """
        Adds a neighbor between this atom and another specified atom.

        Parameters
        ----------
        other_atom : Atom
            The other atom to which a neighbor is added.
        """
        self.neighbors.append(other_atom)
        self.periodicity.append(periodicity)

    def add_not_filtered_neighbor(self, other_atom):
        """
        Adds a neighbor between this atom and another specified atom.

        Parameters
        ----------
        other_atom : Atom
            The other atom to which a neighbor is added.
        """
        self.not_filtered_neighbors.append(other_atom)

    def remove_too_far_neighbors(self, distances):
        """
        Removes a neighbor between this atom and another specified atom.

        Parameters
        ----------
        other_atom : Atom
            The other atom from which the neighbor is removed.
        """
        new_list = []
        k = 0
        for other_atom in self.not_filtered_neighbors:
            for cutoff in self.cutoffs:
                if self.element == cutoff["element1"]:
                    if other_atom.element == cutoff["element2"]:
                        rcut = cutoff["value"]
                if self.element == cutoff["element2"]:
                    if other_atom.element == cutoff["element1"]:
                        rcut = cutoff["value"]

            rij = distances[k]
            k += 1
            if rij > rcut:
                pass
            elif rij == 0.0:
                pass
            else:
                new_list.append(other_atom)
        self.not_filtered_neighbors = new_list

    def get_correlation_length(self):
        """Returns the correlation length associated with the atom."""
        return self.correlation_length

    def get_atomic_mass(self):
        """Returns the atomic mass associated with the atom."""
        return self.atomic_mass

    def calculate_coordination(self):
        """Calculates the coordination associated with the atom."""
        self.coordination = len(self.neighbors)

    def get_coordination(self):
        """Returns the coordination associated with the atom."""
        return self.coordination

    def get_cluster_id(self):
        """Returns the id of the cluster which the atom belongs to."""
        return self.cluster_id

    def set_cluster_id(self, coordination_1, coordination_2, cluster_id):
        """Sets the id of the cluster which the atom belongs to."""
        self.cluster_type.append(f"{coordination_1}-{coordination_2}")
        self.cluster_id = cluster_id
    
    def set_stichovite_cluster_id(self, coordination_1, coordination_2, cluster_id):
        """Sets the id of the cluster which the atom belongs to."""
        self.cluster_type.append(f"stichovite")
        self.cluster_id = cluster_id

    def reset_cluster_id(self):
        """Resets the id of the cluster which the atom belongs to."""
        self.parent = self
        self.cluster_id = None

    def compute_unwrapped_positions(self, cluster_index, box_size):
        """
        Computes unwrapped positions for all atoms in the cluster.

        Parameters:
        ----------
        - cluster_index (int): Identifier of the cluster to which the atom belongs.
        - box_size (tuple): Dimensions of the periodic box in 3D space.

        Returns:
        ----------
        - dict: Dictionary containing atom IDs as keys and unwrapped positions as values.
        """
        if self.cluster_id != cluster_index:
            raise ValueError(
                "Atom does not belong to any cluster. Run find_clusters first."
            )

        # Dictionary to store unwrapped positions for each Atom in the cluster
        unwrapped_positions = {self.id: self.position}

        # Perform DFS traversal to compute unwrapped positions
        stack = [self]

        while tqdm(
            stack, desc="Unwrapping atomic positions", colour="YELLOW", leave=False
        ):
            current_atom = stack.pop()
            for first_neighbor in current_atom.neighbors:
                for second_neighbor in first_neighbor.neighbors:
                    if (
                        second_neighbor.id not in unwrapped_positions
                        and second_neighbor.cluster_id == self.cluster_id
                    ):
                        # Compute relative position from the current atom to its second_neighbor
                        relative_position = self.unwrap_position(
                            second_neighbor.position - current_atom.position, box_size
                        )

                        # Accumulate relative position to get unwrapped position
                        unwrapped_positions[second_neighbor.id] = (
                            unwrapped_positions[current_atom.id] + relative_position
                        )

                        stack.append(second_neighbor)

        return unwrapped_positions

    def unwrap_position(self, position, box_size):
        """
        Unwraps position considering periodic boundary conditions.

        Parameters:
        ----------
        - position: Tuple or list representing the current position in 3D space.
        - box_size: Tuple or list representing the dimensions of the periodic box in 3D space.

        Returns:
        ----------
        - Unwrapped position as a tuple.
        """
        unwrapped_position = []
        for i in range(3):  # Assuming 3D space
            delta = position[i] - round(position[i] / box_size[i]) * box_size[i]
            unwrapped_position.append(delta)
        return tuple(unwrapped_position)
    
    def count_number_of_edge_sharing(self):
        """
        Counts the number of edge sharings of a Silicon (specific of SiO2 glass.)
        """
        unique_bond = [self.id]
        for first_neighbor in self.neighbors: # Loop over oxygen first neighbors
            for second_neighbor in first_neighbor.neighbors:
                if second_neighbor.id != self.id:
                    unique_bond.append(second_neighbor.id)
        
        unique_bond = np.array(unique_bond)
        if self.element=='Si':
            unique_bond,counts = np.unique(unique_bond,return_counts=True)
            idx_of_edges = np.where(counts == 2)[0]
            number_of_edges = len(idx_of_edges)
            self.number_of_edge_sharing = number_of_edges
            hold=1