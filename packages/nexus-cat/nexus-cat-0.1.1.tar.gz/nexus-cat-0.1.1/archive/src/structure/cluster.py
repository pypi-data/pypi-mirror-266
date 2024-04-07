import numpy as np
import os


class Cluster:
    """
    Cluster class representing a cluster of atoms in a molecular system.

    This class contains methods for managing and analyzing clusters, including calculating properties
    such as the center of mass, gyration radius, percolation probability, and writing cluster information to an XYZ file.

    Parameters:
    ----------
    - atoms (list): List of Atom objects representing the atoms in the cluster.
    - box (Box): Box object representing the simulation box.
    - type (str): Type of the cluster.
    - id (int): Unique identifier for the cluster.
    - configuration (str): Configuration of the cluster.
    - size (int): Number of atoms in the cluster.
    - number_of_bonded_polyhedra (int): Number of bonded polyhedra in the cluster.

    Attributes:
    ----------
    - atoms (list): List of Atom objects representing the atoms in the cluster.
    - box (Box): Box object representing the simulation box.
    - type (str): Type of the cluster.
    - id (int): Unique identifier for the cluster.
    - configuration (str): Configuration of the cluster.
    - size (int): Number of atoms in the cluster.
    - number_of_bonded_polyhedra (int): Number of bonded polyhedra in the cluster.
    - continuous (bool): Flag indicating whether the cluster is continuous.
    - center_of_mass (numpy.ndarray): Array representing the center of mass of the cluster.
    - indices (list): List of indices of atoms in the cluster.
    - all_indices (numpy.ndarray): Array of all unique indices of atoms and their neighbors in the cluster.
    - unwrapped_positions (numpy.ndarray): Array of unwrapped positions of atoms in the cluster.
    - percolation_probability (str): String representing percolation probability in different dimensions.
    - gyration_radius (float): Gyration radius of the cluster.

    Methods:
    ----------
    - add_atom(atom): Add an atom to the cluster.
    - get_atoms(): Get the list of atoms in the cluster.
    - set_all_indices(): Set the array of all unique indices of atoms and their neighbors in the cluster.
    - set_unwrapped_positions(positions_dict): Set the unwrapped positions of atoms in the cluster.
    - check_continuity(): Check if the cluster is continuous.
    - calculate_center_of_mass(): Calculate the center of mass of the cluster.
    - write_xyz(path_to_directory): Write cluster information to an XYZ file.
    - calculate_gyration_radius(): Calculate the gyration radius of the cluster.
    - calculate_percolation_probability(): Calculate the percolation probability of the cluster.

    """

    def __init__(
        self,
        atoms=None,
        box=None,
        type="",
        id=None,
        configuration=None,
        size=None,
        number_of_bonded_polyhedra=None,
    ):
        """
        Initialize the Cluster.

        Parameters:
        ----------
        - atoms (list): List of Atom objects representing the atoms in the cluster.
        - box (Box): Box object representing the simulation box.
        - type (str): Type of the cluster.
        - id (int): Unique identifier for the cluster.
        - configuration (str): Configuration of the cluster.
        - size (int): Number of atoms in the cluster.
        - number_of_bonded_polyhedra (int): Number of bonded polyhedra in the cluster.
        """
        self.atoms = atoms if atoms is not None else []
        self.box = box
        self.type = type
        self.id = id
        self.configuration = configuration
        self.size = size
        self.number_of_bonded_polyhedra = number_of_bonded_polyhedra
        self.continuous = True
        self.center_of_mass = []
        self.indices = []
        self.all_indices = []
        self.unwrapped_positions = []
        self.percolation_probability = ""
        self.gyration_radius = 0

    def add_atom(self, atom):
        """
        Add an atom to the cluster.

        Parameters:
        - atom (Atom): Atom object to be added to the cluster.
        """
        self.atoms.append(atom)
    
    def delete_atom(self, atom):
        """
        Delete an atom from the cluster.

        Parameters:
        - atom (Atom): Atom object to be deleted from the cluster.
        """
        if atom in self.atoms:
            self.atoms.remove(atom)

    def get_atoms(self):
        """
        Get the list of atoms in the cluster.

        Returns:
        - list: List of Atom objects representing the atoms in the cluster.
        """
        return self.atoms

    def set_all_indices(self):
        """
        Set the array of all unique indices of atoms and their neighbors in the cluster.
        """
        neighbors = []
        for atom in self.atoms:
            neighbors.append(atom.neighbors)
        neighbors = np.array(neighbors).reshape(-1, 1)
        neighbors = neighbors.reshape(len(neighbors))
        main_indices = [atom.id for atom in self.atoms]
        neighbors_indices = [atom.id for atom in neighbors]
        unique_indices = np.concatenate(
            (np.array(main_indices), np.array(neighbors_indices))
        )
        unique_indices = np.unique(np.array(unique_indices))
        self.all_indices = unique_indices

    def set_unwrapped_positions(self, positions_dict):
        """
        Set the unwrapped positions of atoms in the cluster.

        Parameters:
        - positions_dict (dict): Dictionary containing atom IDs as keys and unwrapped positions as values.
        """
        for atom_id, position in positions_dict.items():
            self.indices.append(atom_id)
            self.unwrapped_positions.append([position[0], position[1], position[2]])

        self.unwrapped_positions = np.array(self.unwrapped_positions)

    def check_continuity(self):
        """
        Check if the cluster is continuous.
        """
        for atom in self.atoms:
            for i in range(len(atom.periodicity)):
                idx = np.where(atom.periodicity[i] != 0)[0]
                if len(idx) != 0:
                    self.continuous = False
                    return
        self.continuous = True

    def calculate_center_of_mass(self):
        """
        Calculate the center of mass of the cluster.
        """
        positions = np.array([atom.position for atom in self.atoms])
        self.center_of_mass = np.mean(positions, axis=0)

    def write_xyz(self, path_to_directory):
        """
        Write cluster information to an XYZ file.

        Parameters:
        - path_to_directory (str): Path to the directory where the XYZ file will be saved.
        """
        simulation_box = self.box.get_box_dimensions(self.configuration)
        with open(
            os.path.join(
                path_to_directory,
                f"unwrap_cluster_{self.type}_{self.id}_{self.configuration}.xyz",
            ),
            "w",
        ) as inp:
            neighbors = []
            atoms = []
            for atom in self.iatoms:
                neighbors.append(atom.neighbors)
                atoms.append(atom)
            neighbors = np.array(neighbors).reshape(-1, 1)
            neighbors = neighbors.reshape(len(neighbors))
            unique_indices = [atom.id for atom in neighbors]
            unique_indices = np.unique(np.array(unique_indices))
            for i in range(len(unique_indices)):
                for atom in neighbors:
                    if unique_indices[i] == atom.id:
                        atoms.append(atom)

            inp.write(
                f'{len(atoms)}\nLattice="{simulation_box[0]} 0.0 0.0 0.0 {simulation_box[1]} 0.0 0.0 0.0 {simulation_box[2]}"\n'
            )
            for atom in atoms:
                inp.write(
                    f"{atom.element} {atom.id} {atom.unwrapped_position[0]} {atom.unwrapped_position[1]} {atom.unwrapped_position[2]}\n"
                )

    def calculate_gyration_radius(self):
        """
        Calculate the gyration radius of the cluster.
        """
        self.gyration_radius = 0
        for i in range(self.unwrapped_positions.shape[0]):
            squared_rij = (np.linalg.norm(self.unwrapped_positions[i, :] - self.unwrapped_positions[:, :],axis=1,)** 2)
            self.gyration_radius += np.sum(squared_rij)

        self.gyration_radius = np.sqrt((0.5 / (self.size**2)) * self.gyration_radius)

    def calculate_percolation_probability(self):
        """
        Calculate the percolation probability of the cluster.
        """
        percolation_x, percolation_y, percolation_z = False, False, False
        box_size = self.box.get_box_dimensions(self.configuration)

        for i in range(self.unwrapped_positions.shape[0]):
            dx = np.abs(self.unwrapped_positions[i, 0] - self.unwrapped_positions[:, 0])
            dy = np.abs(self.unwrapped_positions[i, 1] - self.unwrapped_positions[:, 1])
            dz = np.abs(self.unwrapped_positions[i, 2] - self.unwrapped_positions[:, 2])

            dx = np.max(dx)
            dy = np.max(dy)
            dz = np.max(dz)

            if dx > box_size[0]:
                percolation_x = True
            if dy > box_size[1]:
                percolation_y = True
            if dz > box_size[2]:
                percolation_z = True

        if percolation_x:
            self.percolation_probability += "x"
        if percolation_y:
            self.percolation_probability += "y"
        if percolation_z:
            self.percolation_probability += "z"
