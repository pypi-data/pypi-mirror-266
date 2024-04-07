import numpy as np
from scipy.spatial import cKDTree
from tqdm import tqdm
from itertools import combinations_with_replacement


class StructuralAnalyzer:
    """
    A class for analyzing the structural properties of a molecular system.

    Parameters
    ----------
    system : System object
        The molecular system.

    Methods
    -------
    pair_distribution_function(type1, type2, bin_count=100, max_distance=10.0)
        Computes the pair distribution function for a specific pair of atom types.
    compute_bond_angular_distribution(type1, type2, type3, rcut12, rcut23, bin_count=100)
        Computes the bond angular distribution for a set of three atom types.
    ...

    Attributes
    ----------
    system : System object
        The molecular system used for structural analysis.
    box : Box object
        The simulation box containing the molecular system.

    Examples
    --------
    >>> from clstr.src.system import System
    >>> from StructuralAnalyzer import StructuralAnalyzer

    >>> system = System()  # Assuming System is the class handling molecular systems
    >>> analyzer = StructuralAnalyzer(system, box)

    #### Compute pair distribution function for a specific pair
    >>> pdf = analyzer.pair_distribution_function('Si', 'O')

    #### Compute bond angular distribution for a specific set of atom types
    >>> bad = analyzer.compute_bond_angular_distribution('Si', 'O', 'H', 4.0, 5.0)
    """

    def __init__(self, system, total_number_of_configurations):
        """
        Initialize the StructuralAnalyzer object.

        Parameters
        ----------
        system : System object
            The molecular system.
        """
        self.system = system
        self.number_of_configurations = total_number_of_configurations

    def pair_distribution_function(self):
        def apply_pbc(box_length, diff_vector):
            diff_vector[diff_vector > box_length / 2] -= box_length
            diff_vector[diff_vector <= -box_length / 2] += box_length
            return diff_vector

        # Default parameters
        bins = 300
        lbox = self.system.box.get_box_dimensions()[0]
        r_max = 10.0 if lbox > 20.0 else lbox / 2

        # Extract unique elements and the number of atoms of each type
        unique_element, counts = self.system.get_unique_elements()
        pairs = combinations_with_replacement(unique_element, 2)

        for c in range(self.number_of_configurations):
            positions, mask = self.system.get_positions_at_configuration(c)

            positions = self.wrap_positions_inside_box(
                positions, self.system.box.get_box_dimensions()
            )

    def wrap_positions_inside_box(self, positions, box_size):
        """
        Wrap atomic positions inside the simulation box using periodic boundary conditions.

        Parameters:
        - positions: Array containing atomic positions, where each row represents an atom and each column represents a dimension.
        - box_size: List/array representing the size of the simulation box in each dimension.

        Returns:
        - wrapped_positions: Array containing the wrapped atomic positions inside the simulation box.
        """

        wrapped_positions = positions.copy()  # Create a copy of the positions to modify

        for i in range(len(box_size)):
            # Apply periodic boundary conditions for each dimension
            wrapped_positions[:, i] = np.mod(
                wrapped_positions[:, i] + box_size[i], box_size[i]
            )

        return wrapped_positions
