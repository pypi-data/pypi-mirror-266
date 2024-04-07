import numpy as np
from tqdm import tqdm


class System:
    """
    The System class represents a molecular system containing atoms and their interactions.

    Attributes
    ----------
    atoms : list
        List of atoms present in the system.
    bonds : list
        List of bonds connecting the atoms in the system.
    neighbors : list
        List of Neighbors objects representing relationships between atoms and their neighbors.
    clusters : list
        List of clusters present in the system.
    box : object
        An object representing the simulation box dimensions.

    Methods
    -------
    __init__(atoms=None, bonds=None, neighbors=None, box=None)
        Initializes a System object with the provided atoms, bonds, and neighbors relationships.
    add_atom(atom)
        Adds an atom to the system.
    remove_atom(atom)
        Removes an atom from the system along with its associated bonds and neighbors.
    add_bond(bond)
        Adds a bond between two atoms in the system.
    remove_bond(bond)
        Removes a bond between two atoms in the system.
    add_neighbors(neighbors)
        Adds a Neighbors object representing the relationship between atoms.
    remove_neighbors(neighbors)
        Removes a Neighbors object representing the relationship between atoms.
    add_cluster(cluster)
        Adds a cluster to the system.
    remove_cluster(cluster)
        Removes a cluster from the system.
    get_atoms()
        Returns the list of atoms in the system.
    get_bonds()
        Returns the list of bonds in the system.
    get_neighbors()
        Returns the list of Neighbors objects in the system.
    get_positions_at_configuration(configuration)
        Returns the list of positions of Atom objects at the desired configuration.
    get_positions_by_type(element, configuration)
        Returns the list of positions of Atom objects of the same type and at the desired configuration.
    get_atoms_at_configuration(configuration)
        Returns the list of Atom objects at the desired configuration.
    get_atoms_by_type(element, configuration)
        Returns the list of Atom objects belonging to the same species at the desired configuration.
    get_all_positions_by_type(element)
        Returns the list of positions of all Atom objects of the same type and for all configurations.
    get_unique_elements()
        Returns the unique elements present in the system along with their counts.
    reset_cluster_indexes()
        Resets the cluster indexes for all atoms in the system.
    wrap_self_positions()
        Wraps atomic positions inside the simulation box using periodic boundary conditions.
    """

    def __init__(self, atoms=None, bonds=None, neighbors=None, box=None):
        """
        Initializes a System object with the provided atoms, bonds, and neighbors relationships.

        Parameters
        ----------
        atoms : list, optional
            List of atoms present in the system (default is None).
        bonds : list, optional
            List of bonds connecting the atoms in the system (default is None).
        neighbors : list, optional
            List of Neighbors objects representing relationships between atoms and their neighbors (default is None).
        box : object, optional
            An object representing the simulation box dimensions (default is None).
        """
        self.atoms = atoms if atoms is not None else []
        self.bonds = bonds if bonds is not None else []
        self.neighbors = neighbors if neighbors is not None else []
        self.box = box if box is not None else []
        self.clusters = []


    def add_atom(self, atom):
        """Adds an atom to the system."""
        self.atoms.append(atom)

    def remove_atom(self, atom):
        """Removes an atom from the system along with its associated bonds and neighbors."""
        if atom in self.atoms:
            self.atoms.remove(atom)

    def add_bond(self, bond):
        """Adds a bond between two atoms in the system."""
        self.bonds.append(bond)

    def remove_bond(self, bond):
        """Removes a bond between two atoms in the system."""
        if bond in self.bonds:
            self.bonds.remove(bond)

    def add_neighbors(self, neighbors):
        """Adds a Neighbors object representing the relationship between atoms."""
        self.neighbors.append(neighbors)

    def remove_neighbors(self, neighbors):
        """Removes a Neighbors object representing the relationship between atoms."""
        if neighbors in self.neighbors:
            self.neighbors.remove(neighbors)

    def add_cluster(self, cluster):
        """Adds a cluster to the system."""
        self.clusters.append(cluster)

    def remove_cluster(self, cluster):
        """Removes a cluster from the system."""
        if cluster in self.clusters:
            self.clusters.remove(cluster)

    def get_atoms(self):
        """Returns the list of atoms in the system."""
        return self.atoms

    def get_bonds(self):
        """Returns the list of bonds in the system."""
        return self.bonds

    def get_neighbors(self):
        """Returns the list of Neighbors objects in the system."""
        return self.neighbors

    def get_positions_at_configuration(self, configuration):
        """Returns the list of positions of all Atom objects at the desired configuration."""
        filtered_positions = list(
            map(
                lambda atom: atom.position,
                filter(
                    lambda atom: hasattr(atom, "configuration")
                    and atom.configuration == configuration,
                    self.atoms,
                ),
            )
        )
        filtered_elements = list(
            map(
                lambda atom: atom.element,
                filter(
                    lambda atom: hasattr(atom, "configuration")
                    and atom.configuration == configuration,
                    self.atoms,
                ),
            )
        )
        return np.array(filtered_positions), np.array(filtered_elements)

    def get_positions_by_type(self, element, configuration):
        """Returns the list of positions of all Atom objects of the same type and at the desired configuration."""
        filtered_positions = list(
            map(
                lambda atom: atom.position,
                filter(
                    lambda atom: hasattr(atom, "configuration")
                    and atom.configuration == configuration
                    and atom.element == element,
                    self.atoms,
                ),
            )
        )
        return np.array(filtered_positions)

    def get_atoms_at_configuration(self, configuration):
        """Returns the list of Atom objects at the desired configuration."""
        filtered_atoms = list(
            filter(
                lambda atom: hasattr(atom, "configuration")
                and atom.configuration == configuration,
                self.atoms,
            )
        )
        return filtered_atoms

    def get_atoms_by_type(self, element, configuration):
        """Returns the list of Atom objects belonging to the same species at the desired configuration."""
        filtered_atoms = list(
            filter(
                lambda atom: hasattr(atom, "configuration", "element")
                and atom.configuration == configuration
                and atom.element == element,
                self.atoms,
            )
        )
        return filtered_atoms

    def get_all_positions_by_type(self, element):
        """Returns the list of positions of all Atom objects of the same type and for all configurations."""
        filtered_positions = list(
            map(
                lambda atom: atom.position,
                filter(
                    lambda atom: hasattr(atom, "element") and atom.element == element,
                    self.atoms,
                ),
            )
        )
        return filtered_positions

    def get_unique_elements(self):
        """Returns the unique elements present in the system along with their counts."""
        filtered_elements = np.array(
            list(
                map(
                    lambda atom: atom.element,
                    filter(
                        lambda atom: hasattr(atom, "configuration")
                        and atom.configuration == 0,
                        self.atoms,
                    ),
                )
            )
        )
        return np.unique(filtered_elements, return_counts=True)

    def reset_cluster_indexes(self):
        """Resets the cluster indexes for all atoms in the system."""
        for atom in self.atoms:
            atom.reset_cluster_id()

    def wrap_self_positions(self):
        """Wraps atomic positions inside the simulation box using periodic boundary conditions."""
        for atom in tqdm(
            self.atoms,
            desc="Wrapping positions inside the box ...",
            colour="GREEN",
            leave=False,
        ):
            box_size = self.box.get_box_dimensions(atom.configuration)
            for i in range(len(box_size)):
                # Apply periodic boundary conditions for each dimension
                atom.position[i] = np.mod(atom.position[i] + box_size[i], box_size[i])

    def compute_system_mass(self):
        """Returns the molecular mass of the system."""
        filtered_atoms = self.get_atoms_at_configuration(0)
        mass = 0
        for atom in filtered_atoms:
            mass += atom.atomic_mass

        return mass
