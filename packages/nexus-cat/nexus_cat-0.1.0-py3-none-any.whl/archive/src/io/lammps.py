import numpy as np
from clstr.src.structure.system import System
from clstr.src.structure.atom import Atom


def read_lammps(path_file, number_of_atoms, configuration_range, atoms, cutoffs):
    """
    Reads a LAMMPS data file and imports its content into the program.

    Parameters
    ----------
    path_file : str
        The file path of the LAMMPS data file.
    number_of_atoms : int
        The total number of atoms in the system.
    configuration_range : int or str
        The range of configurations to read. If int, reads the specified number of configurations.
        If str, currently not implemented.

    Returns
    -------
    System or None
        Returns a System object containing the read atoms if successful. Returns None if failed.

    Notes
    -----
    This function reads an LAMMPS file and extracts atom information to create a System object.
    If configuration_range is an int, it reads the specified number of configurations.
    Currently, configuration_range as a string is not implemented.
    """
    if isinstance(configuration_range, int):
        c, n, s = (
            -1,
            0,
            0,
        )  # Initialize variables for configuration, atom count, and system count
        system = System()  # Create an empty System object to store atoms
        with open(path_file, "r", encoding="utf-8") as input:
            for i, line in enumerate(input):
                try:
                    if (
                        line.split(".")[0] == " Atoms"
                    ):  # Check if the line contains 'Lattice'
                        c += 1  # Increase the configuration count
                        n = 0  # Reset the atom count for the new configuration
                        s += 1  # Increment system count for each new 'Lattice' line
                        pass
                except:
                    print(
                        "Failed to read the LAMMPS data file.\nPlease check 'Input file format' in parameter file."
                    )
                    return None
                try:
                    if (
                        line.split()[0] != str(number_of_atoms)
                        and line.split(".")[0] != " Atoms"
                    ):
                        # If the line does not contain the total number of atoms or 'Lattice'
                        parts = line.split()
                        x = float(parts[1])
                        y = float(parts[2])
                        z = float(parts[3])
                        position = np.array([x, y, z])
                        for atom in atoms:
                            if int(parts[0]) == atom["alias"]:
                                element = atom["element"]
                        this_atom = Atom(
                            element, n, position, 0, c, cutoffs
                        )  # Create an Atom object
                        system.add_atom(this_atom)  # Add the Atom to the System
                        n += 1  # Increment the atom count
                except:
                    pass
        return system, c + 1  # Return the System object and total configuration count
    elif isinstance(configuration_range, str):
        # Not implemented yet.
        return None
