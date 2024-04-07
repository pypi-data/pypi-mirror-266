import sys
import os
import time
import numpy as np
from collections import Counter
from tqdm import tqdm
import pathlib
from clstr.src.io.print_title import print_title
from clstr.src.settings.parameter_file_reader import ParameterFileReader
from clstr.src.settings.settings import Settings
from clstr.src.structure.box import Box
from clstr.src.io.xyz import read_xyz
from clstr.src.io.lammps import read_lammps
from clstr.src.io.build_fancy_recaps import build_fancy_recaps,build_fancy_recaps_stichovite
from clstr.src.structure.neighbor import Neighbors
from clstr.src.analysis.cluster_analyzer import ClusterAnalyzer
from clstr.src.analysis.percolation_analyzer import PercolationAnalyzer


def core(project_name, simulation_box, path_to_data_file, settings):
    """
    The core function handling the analysis of clusters within the provided data.

    Parameters
    ----------
    project_name : str
        Name of the project.
    simulation_box : float
        Size of the simulation box.
    path_to_data_file : str
        Path to the data file.
    settings : Settings object
        Configuration settings.

    Returns
    -------
    None

    Notes
    -----
    This function performs the core analysis of clusters based on provided data and settings.
    It reads and processes the data, performs cluster analysis, and exports the results.
    """

    # Extract settings
    options = settings.get_parameter_value("Options")
    properties = settings.get_parameter_value("Properties")
    cutoffs = settings.get_parameter_value("Cutoffs")

    if len(properties)>1:
        raise ValueError("Only one mode is expected in section Properties. Please verify json configuration file.")
        sys.exit()

    cutoff_values = []
    for c in cutoffs:
        cutoff_values.append(c["value"])
        if c["element1"] != c["element2"]:
            cutoff = c["value"]

    cutoff_max = max(cutoff_values)
    
    for p in properties:
        main_atom = p['connectivity'][0]
        connectivity = p['connectivity']
        neighboring_mode = p['neighboring_mode']
        prop_polyhedra = p['polyhedra']
        poly_keys = range(1,len(prop_polyhedra)+1)

    path_to_export_directory = settings.get_parameter_value("Path to export directory")

    # Create directories if they don't exist and print out content if existing.
    path_to_project_directory = os.path.join(path_to_export_directory, project_name)
    if os.path.exists(path_to_project_directory):
        if "overwrite_results_by_default" in options:
            pass
        else:
            for root, dirs, files in os.walk(path_to_project_directory):
                level = root.replace(path_to_project_directory, "").count(os.sep)
                indent = " " * 4 * (level)
                print("|{}{}/".format(indent, os.path.basename(root)))
                subindent = " " * 4 * (level + 1)
                for f in files:
                    print("|{}{}".format(subindent, f))
            print("\n")
            displayWarningMsg = (
                "The existing files will be eventually overwrited, continue ? [y/n]:"
            )
            if input(displayWarningMsg) == "y":
                pass
            else:
                print("\n")
                print("Exiting calculations ...")
                print("\n")
                sys.exit()
    else:
        pathlib.Path(path_to_project_directory).mkdir(parents=True, exist_ok=True)

    # Create a simulation box
    if settings.get_parameter_value("Input file format") != "XYZ":
        box = Box(simulation_box, simulation_box, simulation_box)

    # Extract information from settings
    total_number_of_atoms = settings.get_parameter_value("Total number of atoms")
    range_of_configurations_to_analyze = settings.get_parameter_value(
        "Range of configuration to analyze"
    )

    atoms = settings.get_parameter_value("Atoms")

    input_file_format = settings.get_parameter_value("Input file format")

    # Read data based on file format
    if input_file_format == "XYZ":
        system, total_number_of_configurations, box = read_xyz(
            path_to_data_file,
            total_number_of_atoms,
            range_of_configurations_to_analyze,
            cutoffs,
        )
    elif input_file_format == "LAMMPS":
        system, total_number_of_configurations = read_lammps(
            path_to_data_file,
            total_number_of_atoms,
            range_of_configurations_to_analyze,
            atoms,
            cutoffs,
        )
    else:
        print("WARNING: only XYZ and LAMMPS data file formats are supported for now.")
        sys.exit(1)

    system.box = box
    system.wrap_self_positions()
    cluster_index = 0

    # Analysis loop for each configuration
    for i in tqdm(
        range(total_number_of_configurations),
        desc="Iterates through configurations ...",
        colour="MAGENTA",
        leave=False,
    ):
        # for i in range(total_number_of_configurations):
        these_positions, mask = system.get_positions_at_configuration(i)
        these_atoms = system.get_atoms_at_configuration(i)
        these_neighbors = Neighbors(these_atoms, i, these_positions, mask, mode=neighboring_mode)
        these_neighbors.calculate_neighbors(
            box.get_box_dimensions(i), cutoff, neighboring_mode
        )
        system.add_neighbors(these_neighbors)

        cluster_analyzer = ClusterAnalyzer(these_atoms, box, cluster_index, properties)

        # TODO remove polyhedra for silica only, find a way to make it general.
        # Keep this for now
        polyhedra = dict(zip(poly_keys,prop_polyhedra))

        unique_coordination = {
            atom.coordination for atom in these_atoms if atom.element == main_atom
        }

        # Loop to find clusters based on unique coordination
        cluster_types_found = []
        for key, value in polyhedra.items():
            z1, z2 = value[0], value[1]
            if z1 in unique_coordination and z2 in unique_coordination:
                system.reset_cluster_indexes()

                cluster_types_found.append(f"{z1}-{z2}")

                if z1 == z2:
                    si_clusters,Clusters,number_of_bonded_polyhedra = cluster_analyzer.find_clusters(connectivity, neighboring_mode, z1, z2, mask)
                else:
                    # si_clusters, Clusters, number_of_bonded_polyhedra = cluster_analyzer.find_alternating_clusters('Si', z1, z2)
                    pass  # bugged for now.

                for c in range(len(Clusters)):
                    Clusters[
                        c + 1
                    ].number_of_bonded_polyhedra = number_of_bonded_polyhedra
                    system.add_cluster(Clusters[c + 1])

                # Count clusters
                clusters_distribution = Counter(
                    atom.cluster_id
                    for atom in these_atoms
                    if atom.cluster_id is not None and f"{z1}-{z2}" in atom.cluster_type
                )

                clusters_by_count = {}
                for cluster, count in clusters_distribution.items():
                    if count not in clusters_by_count:
                        clusters_by_count[count] = [cluster]
                    else:
                        clusters_by_count[count].append(cluster)

                # Write cluster distributions to files
                path_to_clusters_distributions = os.path.join(
                    path_to_project_directory, "clusters_distributions"
                )

                if not os.path.exists(path_to_clusters_distributions):
                    os.mkdir(path_to_clusters_distributions)
                with open(
                    os.path.join(
                        path_to_clusters_distributions,
                        f"clusters_distribution_{z1}-{z2}_{i}.dat",
                    ),
                    "w",
                ) as inp:
                    sorted_clusters = sorted(
                        clusters_by_count.items(),
                        key=lambda item: item[0],
                        reverse=True,
                    )
                    for count, clusters in sorted_clusters:
                        inp.write(
                            f"{len(clusters)} cluster{'s' if len(clusters) > 1 else ''} of {count}\n"
                        )

    if "compute_stichovite_clusters" in options:
        """ specific to SiO2 glasses """
        
        system.reset_cluster_indexes()

        cluster_types_found.append(f"stichovite")

        si_clusters,Clusters,number_of_bonded_polyhedra = cluster_analyzer.find_stichovite_clusters(connectivity, neighboring_mode, 6, 6, mask)

        for c in range(len(Clusters)):
            Clusters[
                c + 1
            ].number_of_bonded_polyhedra = number_of_bonded_polyhedra
            system.add_cluster(Clusters[c + 1])

        # Count clusters
        clusters_distribution = Counter(
            atom.cluster_id
            for atom in these_atoms
            if atom.cluster_id is not None and f"stichovite" in atom.cluster_type
        )

        clusters_by_count = {}
        for cluster, count in clusters_distribution.items():
            if count not in clusters_by_count:
                clusters_by_count[count] = [cluster]
            else:
                clusters_by_count[count].append(cluster)

        # Write cluster distributions to files
        path_to_clusters_distributions = os.path.join(path_to_project_directory, "clusters_distributions")

        if not os.path.exists(path_to_clusters_distributions):
            os.mkdir(path_to_clusters_distributions)
        with open(os.path.join(path_to_clusters_distributions,f"clusters_distribution_stichovite_{i}.dat",),"w",) as inp:
            sorted_clusters = sorted(clusters_by_count.items(),key=lambda item: item[0],reverse=True)
            for count, clusters in sorted_clusters:
                inp.write(
                    f"{len(clusters)} cluster{'s' if len(clusters) > 1 else ''} of {count}\n"
                )
        inp.close()

    percolation_analyzer = PercolationAnalyzer(system.clusters)

    average_clusters_size = np.zeros(
        (total_number_of_configurations, len(cluster_types_found))
    )
    correlation_length = np.zeros(
        (total_number_of_configurations, len(cluster_types_found))
    )
    maximum_gyration_radius = np.zeros(
        (total_number_of_configurations, len(cluster_types_found))
    )
    spanning_cluster_size = np.zeros(
        (total_number_of_configurations, len(cluster_types_found))
    )
    order_parameter_p_infinite = np.zeros(
        (total_number_of_configurations, len(cluster_types_found))
    )
    percolation_1D = np.zeros(
        (total_number_of_configurations, len(cluster_types_found))
    )
    percolation_2D = np.zeros(
        (total_number_of_configurations, len(cluster_types_found))
    )
    percolation_3D = np.zeros(
        (total_number_of_configurations, len(cluster_types_found))
    )
    biggest_cluster_size = np.zeros(
        (total_number_of_configurations, len(cluster_types_found))
    )
    average_gyration_radius = np.zeros((total_number_of_configurations, len(cluster_types_found)))

    for i in tqdm(
        range(total_number_of_configurations),
        desc="Performing percolation analysis ...",
        colour="MAGENTA",
        leave=False,
    ):
        for j in range(len(cluster_types_found)):
            results = percolation_analyzer.calculate_clusters_properties(
                cluster_types_found[j], i, 
            )

            average_clusters_size[i][j] = results[0]
            correlation_length[i][j] = results[1]
            maximum_gyration_radius[i][j] = results[2]
            spanning_cluster_size[i][j] = results[3]
            order_parameter_p_infinite[i][j] = results[4]
            percolation_1D[i][j] = results[5]
            percolation_2D[i][j] = results[6]
            percolation_3D[i][j] = results[7]
            biggest_cluster_size[i][j] = results[8]

    time_averaged_average_clusters_size = np.mean(average_clusters_size, axis=0)
    time_averaged_correlation_length = np.mean(correlation_length, axis=0)
    time_averaged_maximum_gyration_radius = np.mean(maximum_gyration_radius, axis=0)
    time_averaged_spanning_cluster_size = np.mean(spanning_cluster_size, axis=0)
    time_averaged_order_parameter_p_infinite = np.mean(
        order_parameter_p_infinite, axis=0
    )
    time_averaged_percolation_1D = np.mean(percolation_1D, axis=0)
    time_averaged_percolation_2D = np.mean(percolation_2D, axis=0)
    time_averaged_percolation_3D = np.mean(percolation_3D, axis=0)
    time_averaged_biggest_cluster_size = np.mean(biggest_cluster_size, axis=0)

    file_average_clusters_size = open(
        os.path.join(path_to_project_directory, "average_clusters_size.dat"), "w"
    )
    file_correlation_length = open(
        os.path.join(path_to_project_directory, "correlation_length.dat"), "w"
    )
    file_maximum_gyration_radius = open(
        os.path.join(path_to_project_directory, "maximum_gyration_radius.dat"), "w"
    )
    file_spanning_cluster_size = open(
        os.path.join(path_to_project_directory, "spanning_cluster_size.dat"), "w"
    )
    file_order_parameter_p_infinite = open(
        os.path.join(path_to_project_directory, "order_parameter_p_infinite.dat"), "w"
    )
    file_percolation_1D = open(
        os.path.join(path_to_project_directory, "percolation_1D.dat"), "w"
    )
    file_percolation_2D = open(
        os.path.join(path_to_project_directory, "percolation_2D.dat"), "w"
    )
    file_percolation_3D = open(
        os.path.join(path_to_project_directory, "percolation_3D.dat"), "w"
    )
    file_biggest_cluster_size = open(
        os.path.join(path_to_project_directory, "biggest_cluster_size.dat"), "w"
    )


    for j in range(len(cluster_types_found)):
        file_average_clusters_size.write(
            f"{time_averaged_average_clusters_size[j]} # {cluster_types_found[j]}\n"
        )
        file_correlation_length.write(
            f"{time_averaged_correlation_length[j]} # {cluster_types_found[j]}\n"
        )
        file_maximum_gyration_radius.write(
            f"{time_averaged_maximum_gyration_radius[j]} # {cluster_types_found[j]}\n"
        )
        file_spanning_cluster_size.write(
            f"{time_averaged_spanning_cluster_size[j]} # {cluster_types_found[j]}\n"
        )
        file_order_parameter_p_infinite.write(
            f"{time_averaged_order_parameter_p_infinite[j]} # {cluster_types_found[j]}\n"
        )
        file_percolation_1D.write(
            f"{time_averaged_percolation_1D[j]} # {cluster_types_found[j]}\n"
        )
        file_percolation_2D.write(
            f"{time_averaged_percolation_2D[j]} # {cluster_types_found[j]}\n"
        )
        file_percolation_3D.write(
            f"{time_averaged_percolation_3D[j]} # {cluster_types_found[j]}\n"
        )
        file_biggest_cluster_size.write(
            f"{time_averaged_biggest_cluster_size[j]} # {cluster_types_found[j]}\n"
        )
        gyration_radius = []
        sizes = []
        average_gyration_radius = {}
        for cluster in system.clusters:
            if cluster.type == cluster_types_found[j] and len(cluster.percolation_probability) == 0:
                gyration_radius.append(cluster.gyration_radius)
                sizes.append(cluster.size)
        gyration_radius = np.array(gyration_radius)
        sizes = np.array(sizes)
        for size in np.unique(sizes):
            indices = np.where(sizes==size)
            average_radius = np.mean(gyration_radius[indices])
            average_gyration_radius[size] = average_radius
        
        filename = f"average_gyration_radius-{cluster_types_found[j]}.dat"
        file_average_gyration_radius = open(
        os.path.join(path_to_project_directory, filename), "w"
        ) 
        
        for size,average_radius in average_gyration_radius.items():
            file_average_gyration_radius.write(f"{size}\t{average_radius}\n")

    file_average_clusters_size.close()
    file_correlation_length.close()
    file_maximum_gyration_radius.close()
    file_spanning_cluster_size.close()
    file_order_parameter_p_infinite.close()
    file_percolation_1D.close()
    file_percolation_2D.close()
    file_percolation_3D.close()
    file_biggest_cluster_size.close()
    file_average_gyration_radius.close()
            
    return system


if __name__ == "__main__":

    # Read settings from parameter file
    print_title()
    start = time.time()
    settings = Settings()
    configuration_file_path = sys.argv[1]
    if not os.path.exists(configuration_file_path):
        raise ValueError("Path to configuration file given in argument is not found.")
    parameter_file_reader = ParameterFileReader(configuration_file_path)
    print(
        f"   INFO: starting analysis with parameter file\n\t--->\t{configuration_file_path}"
    )
    parameters = parameter_file_reader.create_parameters()
    if parameters:
        for param in parameters:
            settings.add_parameter(param)

    multiple_trajectories = settings.get_parameter_value("Multiple trajectories")
    options = settings.get_parameter_value("Options")
    path_to_export_directory = settings.get_parameter_value("Path to export directory")

    # Process multiple trajectories if needed
    if multiple_trajectories == True:
        project_name = settings.get_parameter_value("Project name")
        # Read content from project files
        file1 = open(os.path.join(os.getcwd(), project_name))
        lines1 = file1.readlines()
        lines1 = [line.strip() for line in lines1]

        simulation_box = settings.get_parameter_value("Simulation box")
        file2 = open(os.path.join(os.getcwd(), simulation_box))
        lines2 = file2.readlines()
        lines2 = [float(line.strip()) for line in lines2]

        path_to_data_file = settings.get_parameter_value("Path to data file")
        file3 = open(os.path.join(os.getcwd(), path_to_data_file))
        lines3 = file3.readlines()
        lines3 = [line.strip() for line in lines3]

        # Process and analyze for each set of project files
        if len(lines1) == len(lines2) == len(lines3):
            progress_bar = tqdm(range(len(lines1)),desc=f"Iterates through files ...",colour="YELLOW",leave=True)
            for t in progress_bar:
                project_name = lines1[t]
                simulation_box = lines2[t]
                path_to_data_file = lines3[t]

                progress_bar.set_description(f"Iterates through files ---> {path_to_data_file} ")

                system = core(project_name, simulation_box, path_to_data_file, settings)

            if "build_fancy_recaps" in options:
                mass = system.compute_system_mass()
                try:
                    pressure_path = (
                        settings.get_parameter_value("Simulation box").split("boxes")[0]
                        + "pressure"
                    )
                except:
                    pressure_path = None
                if "compute_stichovite_clusters" in options:
                    build_fancy_recaps_stichovite(path_to_export_directory,len(lines1),path_to_pressures=pressure_path,path_to_boxes=os.path.join(os.getcwd(), settings.get_parameter_value("Simulation box")),mass=mass)
                else:
                    build_fancy_recaps(path_to_export_directory,len(lines1),path_to_pressures=pressure_path,path_to_boxes=os.path.join(os.getcwd(), settings.get_parameter_value("Simulation box")),mass=mass)
        else:
            print("\tERROR: input files doesn't have the same number of lines")
        stop = time.time()
        if "print_performances" in options:
            print(f"   INFO: analysis completed in {stop-start:.3f}s")
        print(
            f'   INFO: results exported in directory\n\t--->\t{settings.get_parameter_value("Path to export directory")}'
        )

    else:
        project_name = settings.get_parameter_value("Project name")
        simulation_box = settings.get_parameter_value("Simulation box")
        path_to_data_file = settings.get_parameter_value("Path to data file")

        system = core(project_name, simulation_box, path_to_data_file, settings)
        stop = time.time()
        if "print_performances" in options:
            print(f"   INFO: analysis completed in {stop-start:.3f}s")
        print(
            f'   INFO: results exported in the directory\n\t--->\t{settings.get_parameter_value("Path to export directory")}'
        )
