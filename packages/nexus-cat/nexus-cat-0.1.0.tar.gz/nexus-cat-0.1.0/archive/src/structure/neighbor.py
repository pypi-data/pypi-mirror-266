import numpy as np
from scipy.spatial import cKDTree
from tqdm import tqdm


class Neighbors:
    """
    The Neighbors class represents the relationship between atoms and their neighboring atoms
    within a molecular system.

    Attributes:
    ----------
    - atoms (list): List of the central atoms in the relationship.
    - configuration (str): Configuration identifier for the atoms.
    - positions (list): List of positions of the central atoms.
    - mask (list): List representing the atom types.
    - indices (list): List of indices of central atoms and their neighboring atoms.
    - distances (list): List of distances between the central atom and its neighboring atoms.

    Methods:
    ----------
    - __init__(atoms, configuration, positions=None, mask=None, indices=None, distances=None):
      Initializes a Neighbors object for the central atoms with their neighboring atoms and respective distances.
    - calculate_neighbors(box_size, cutoff):
      Computes neighboring atoms within the specified cutoff radius, considering periodic boundary conditions.
    - add_indices(indices):
      Adds a central atom to the list of indices.
    - add_distances(distances):
      Adds the distances between the central atom and its neighboring atoms to the list of distances.
    - get_atom():
      Returns the central atom.
    - get_indices():
      Returns the list of neighboring atoms.
    - get_distances():
      Returns the list of distances between the central atom and its neighboring atoms.
    - wrap_positions_inside_box(positions, box_size):
      Wraps atomic positions inside the simulation box using periodic boundary conditions.

    """

    def __init__(
        self,
        atoms,
        configuration,
        positions=None,
        mask=None,
        indices=None,
        distances=None,
        mode=None,
    ):
        """
        Initializes a Neighbors object for the central atoms with theirs neighboring atoms and respective distances.

        Parameters:
        ----------
        - atoms (list): List of the central atoms in the relationship.
        - configuration (str): Configuration identifier for the atoms.
        - positions (list): List of positions of the central atoms (default is None).
        - mask (list): List representing the atom types (default is None).
        - indices (list): List of indices of central atoms and their neighboring atoms (default is None).
        - distances (list): List of distances between the central atom and its neighboring atoms (default is None).

        """
        self.atoms = atoms
        self.configuration = configuration
        self.positions = positions if positions is not None else []
        self.mask = mask if mask is not None else []
        self.indices = indices if indices is not None else []
        self.distances = distances if distances is not None else []
        self.mode = mode if mode is not None else 'bond'

    def calculate_neighbors(self, box_size, cutoff, mode):
        """
        Computes neighboring atoms within the specified cutoff radius, considering periodic boundary conditions.

        Parameters:
        ----------
        - box_size (list): Dimensions of the simulation box in each dimension.
        - cutoff (float): Maximum distance between the central atom and its neighboring atoms.

        """

        if mode == 'bond':

            tree = cKDTree(self.positions, boxsize=box_size)

            for i in tqdm(
                range(len(self.positions)),
                colour="RED",
                desc="Computing neighboring atoms",
                leave=False,
            ):
                indices = tree.query_ball_point(self.positions[i], cutoff)

                periodic_diff = np.zeros((3, len(indices)))
                periodic_dir = np.zeros((3, len(indices)))
                for j in range(len(box_size)):
                    diff = self.positions[indices, j] - self.positions[i][j]

                    periodic_diff[j] = np.where(
                        np.abs(diff) > box_size[j] / 2,
                        box_size[j] - np.abs(diff),
                        np.abs(diff),
                    )

                    periodic_dir[j] = np.where(
                        (np.abs(diff) > box_size[j] / 2) & (diff > 0), 1, periodic_dir[j]
                    )
                    periodic_dir[j] = np.where(
                        (np.abs(diff) > box_size[j] / 2) & (diff < 0), -1, periodic_dir[j]
                    )

                norm_distances = np.linalg.norm(periodic_diff, axis=0)

                valid_indices = np.where(
                    (norm_distances <= cutoff) & (self.mask[indices] != self.mask[i])
                )[0]
                filtered_indices = np.array(indices)[valid_indices]
                filtered_distances = norm_distances[valid_indices]

                self.add_indices(filtered_indices)
                self.add_distances(filtered_distances)

                k = 0
                for j in filtered_indices:
                    self.atoms[i].add_neighbor(self.atoms[j], periodic_diff[:, k])
                    k += 1

                self.atoms[i].calculate_coordination()
                
        
        elif mode == 'distance':
            
            tree = cKDTree(self.positions, boxsize=box_size)

            for i in tqdm(
                range(len(self.positions)),
                colour="RED",
                desc="Computing neighboring atoms",
                leave=False,
            ):
                indices = tree.query_ball_point(self.positions[i], cutoff)

                periodic_diff = np.zeros((3, len(indices)))
                periodic_dir = np.zeros((3, len(indices)))
                for j in range(len(box_size)):
                    diff = self.positions[indices, j] - self.positions[i][j]

                    periodic_diff[j] = np.where(
                        np.abs(diff) > box_size[j] / 2,
                        box_size[j] - np.abs(diff),
                        np.abs(diff),
                    )

                    periodic_dir[j] = np.where(
                        (np.abs(diff) > box_size[j] / 2) & (diff > 0), 1, periodic_dir[j]
                    )
                    periodic_dir[j] = np.where(
                        (np.abs(diff) > box_size[j] / 2) & (diff < 0), -1, periodic_dir[j]
                    )

                norm_distances = np.linalg.norm(periodic_diff, axis=0)

                valid_indices = np.where((norm_distances <= cutoff))[0]
                filtered_indices = np.array(indices)[valid_indices]
                filtered_distances = norm_distances[valid_indices]

                self.add_indices(filtered_indices)
                self.add_distances(filtered_distances)

                k = 0
                for j in filtered_indices:
                    self.atoms[i].add_neighbor(self.atoms[j], periodic_diff[:, k])
                    k += 1

                self.atoms[i].calculate_coordination()
                
        for i in tqdm(range(len(self.atoms)),colour="RED",desc="Computing number of edge-sharing per atom",leave=False):
            self.atoms[i].count_number_of_edge_sharing()

    def add_indices(self, indices):
        """Adds a central atom the list of indices"""
        self.indices.append(indices)

    def add_distances(self, distances):
        """Adds the distances betwen central atom and its neighboring atoms to the list of distances"""
        self.distances.append(distances)

    def get_atom(self):
        """Returns the central atom."""
        return self.atom

    def get_indices(self):
        """Returns the list of neighboring atoms."""
        return self.indices

    def get_distances(self):
        """Returns the list of distances between the central atom and its neighboring atoms."""
        return self.distances

    def wrap_positions_inside_box(self, positions, box_size):
        """
        Wrap atomic positions inside the simulation box using periodic boundary conditions.

        Parameters:
        ----------
        - positions: Array containing atomic positions, where each row represents an atom and each column represents a dimension.
        - box_size: List/array representing the size of the simulation box in each dimension.

        Returns:
        ----------
        - wrapped_positions: Array containing the wrapped atomic positions inside the simulation box.
        """

        wrapped_positions = positions.copy()

        for i in range(len(box_size)):
            wrapped_positions[:, i] = np.mod(
                wrapped_positions[:, i] + box_size[i], box_size[i]
            )

        return wrapped_positions
