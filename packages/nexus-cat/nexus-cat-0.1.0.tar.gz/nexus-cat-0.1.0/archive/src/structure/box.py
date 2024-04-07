import numpy as np

class Box:
    """
    The Box class represents an atomic simulation box.

    Attributes
    ----------
    length_x : float
        Length of the box in the x-direction.
    length_y : float
        Length of the box in the y-direction.
    length_z : float
        Length of the box in the z-direction.
    volume : float
        Volume of the box.
    atoms_inside : list
        List of atoms contained within the box.

    Methods
    -------
    __init__(length_x, length_y, length_z)
        Initializes a Box object with specified dimensions.
    get_volume()
        Calculates and returns the volume of the box.
    add_atom(atom)
        Adds an atom to the box.
    get_atoms_inside()
        Returns the list of atoms inside the box.
    get_box_dimensions()
        Returns the dimensions of the box.
    """

    def __init__(self, length_x, length_y, length_z):
        """
        Initializes a Box object with specified dimensions.

        Parameters
        ----------
        length_x : float
            Length of the box in the x-direction.
        length_y : float
            Length of the box in the y-direction.
        length_z : float
            Length of the box in the z-direction.
        """
        self.length_x = np.array(length_x)
        self.length_y = np.array(length_y)
        self.length_z = np.array(length_z)
        self.volume = self.get_volume()
        self.atoms_inside = []

    def get_volume(self):
        """Calculates and returns the volume of the box."""
        return self.length_x * self.length_y * self.length_z

    def get_box_dimensions(self, configuration):
        """Returns the dimensions of the box."""
        return [self.length_x[configuration], self.length_y[configuration], self.length_z[configuration]]
