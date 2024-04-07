import numpy as np
import os, sys


def build_fancy_recaps(
    directory, number, path_to_pressures=None, path_to_boxes=None, mass=None
):
    Boxe, Density, Pressure = [], [], []
    acs4, acs5, acs6 = np.zeros((number)), np.zeros((number)), np.zeros((number))
    bcs4, bcs5, bcs6 = np.zeros((number)), np.zeros((number)), np.zeros((number))
    cl4, cl5, cl6 = np.zeros((number)), np.zeros((number)), np.zeros((number))
    rg4, rg5, rg6 = np.zeros((number)), np.zeros((number)), np.zeros((number))
    pp3D4, pp3D5, pp3D6 = np.zeros((number)), np.zeros((number)), np.zeros((number))
    pp2D4, pp2D5, pp2D6 = np.zeros((number)), np.zeros((number)), np.zeros((number))
    pp1D4, pp1D5, pp1D6 = np.zeros((number)), np.zeros((number)), np.zeros((number))
    pi4, pi5, pi6 = np.zeros((number)), np.zeros((number)), np.zeros((number))
    scs4, scs5, scs6 = np.zeros((number)), np.zeros((number)), np.zeros((number))

    nacs = 0
    nbcs = 0
    ncl = 0
    nrg = 0
    npp3D = 0
    npp2D = 0
    npp1D = 0
    npi = 0
    nscs = 0
    for subdir, dirs, files in os.walk(directory):
        dirs.sort()
        for file in files:
            if file == "average_clusters_size.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                acs4[nacs] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                acs5[nacs] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                acs6[nacs] = float(line.split()[0])
                nacs += 1
            if file == "biggest_cluster_size.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                bcs4[nbcs] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                bcs5[nbcs] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                bcs6[nbcs] = float(line.split()[0])
                nbcs += 1
            if file == "correlation_length.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                cl4[ncl] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                cl5[ncl] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                cl6[ncl] = float(line.split()[0])
                ncl += 1
            if file == "order_parameter_p_infinite.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                pi4[npi] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                pi5[npi] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                pi6[npi] = float(line.split()[0])
                npi += 1
            if file == "maximum_gyration_radius.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                rg4[nrg] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                rg5[nrg] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                rg6[nrg] = float(line.split()[0])
                nrg += 1
            if file == "spanning_cluster_size.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                scs4[nscs] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                scs5[nscs] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                scs6[nscs] = float(line.split()[0])
                nscs += 1
            if file == "percolation_1D.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                pp1D4[npp1D] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                pp1D5[npp1D] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                pp1D6[npp1D] = float(line.split()[0])
                npp1D += 1
            if file == "percolation_2D.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                pp2D4[npp2D] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                pp2D5[npp2D] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                pp2D6[npp2D] = float(line.split()[0])
                npp2D += 1
            if file == "percolation_3D.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                pp3D4[npp3D] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                pp3D5[npp3D] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                pp3D6[npp3D] = float(line.split()[0])
                npp3D += 1

    if path_to_pressures is not None:
        with open(path_to_pressures, "r") as inp:
            for li, l in enumerate(inp):
                Pressure.append(float(l))
        inp.close()
        Pressure = np.array(Pressure)
    else:
        Pressure = [0] * number

    if path_to_boxes is not None:
        with open(path_to_boxes, "r") as inp:
            for li, l in enumerate(inp):
                Boxe.append(float(l))
                dens = mass * 1.66054e-24 / (float(l) * 0.00000001) ** 3
                Density.append(dens)
        inp.close()
        Boxe = np.array(Boxe)
        Density = np.array(Density)
    else:
        Boxe = [0] * number
        Density = [0] * number
    try:
        with open(os.path.join(directory, "AverageClusterSize.dat"), "w") as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], acs4[i], acs5[i], acs6[i]
                    )
                )
    except:
        pass
    try:
        with open(os.path.join(directory, "BiggestClusterSize.dat"), "w") as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], bcs4[i], bcs5[i], bcs6[i]
                    )
                )
    except:
        pass
    try:
        with open(os.path.join(directory, "SpanningClusterSize.dat"), "w") as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], scs4[i], scs5[i], scs6[i]
                    )
                )
    except:
        pass
    try:
        with open(os.path.join(directory, "Pinf.dat"), "w") as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], pi4[i], pi5[i], pi6[i]
                    )
                )
    except:
        pass
    try:
        with open(os.path.join(directory, "RadiiOfGyration.dat"), "w") as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], rg4[i], rg5[i], rg6[i]
                    )
                )
    except:
        pass
    try:
        with open(os.path.join(directory, "CorrelationLength.dat"), "w") as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], cl4[i], cl5[i], cl6[i]
                    )
                )
    except:
        pass
    try:
        with open(
            os.path.join(directory, "PercolationProbability3D.dat"), "w"
        ) as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], pp3D4[i], pp3D5[i], pp3D6[i]
                    )
                )
    except:
        pass
    try:
        with open(
            os.path.join(directory, "PercolationProbability2D.dat"), "w"
        ) as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], pp2D4[i], pp2D5[i], pp2D6[i]
                    )
                )
    except:
        pass
    try:
        with open(
            os.path.join(directory, "PercolationProbability1D.dat"), "w"
        ) as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], pp1D4[i], pp1D5[i], pp1D6[i]
                    )
                )
    except:
        pass

def build_fancy_recaps_stichovite(
    directory, number, path_to_pressures=None, path_to_boxes=None, mass=None
):
    Boxe, Density, Pressure = [], [], []
    acs4, acs5, acs6, acs6stcv  = np.zeros((number)), np.zeros((number)), np.zeros((number)), np.zeros((number))
    bcs4, bcs5, bcs6, bcs6stcv  = np.zeros((number)), np.zeros((number)), np.zeros((number)), np.zeros((number))
    cl4, cl5, cl6, cl6stcv  = np.zeros((number)), np.zeros((number)), np.zeros((number)), np.zeros((number))
    rg4, rg5, rg6, rg6stcv  = np.zeros((number)), np.zeros((number)), np.zeros((number)), np.zeros((number))
    pp3D4, pp3D5, pp3D6, pp3D6stcv  = np.zeros((number)), np.zeros((number)), np.zeros((number)), np.zeros((number))
    pp2D4, pp2D5, pp2D6, pp2D6stcv  = np.zeros((number)), np.zeros((number)), np.zeros((number)), np.zeros((number))
    pp1D4, pp1D5, pp1D6, pp1D6stcv  = np.zeros((number)), np.zeros((number)), np.zeros((number)), np.zeros((number))
    pi4, pi5, pi6, pi6stcv  = np.zeros((number)), np.zeros((number)), np.zeros((number)), np.zeros((number))
    scs4, scs5, scs6, scs6stcv  = np.zeros((number)), np.zeros((number)), np.zeros((number)), np.zeros((number))

    nacs = 0
    nbcs = 0
    ncl = 0
    nrg = 0
    npp3D = 0
    npp2D = 0
    npp1D = 0
    npi = 0
    nscs = 0
    for subdir, dirs, files in os.walk(directory):
        dirs.sort()
        for file in files:
            if file == "average_clusters_size.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                acs4[nacs] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                acs5[nacs] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                acs6[nacs] = float(line.split()[0])
                            if line.split("#")[1] == " stichovite\n":
                                acs6stcv[nacs] = float(line.split()[0])
                nacs += 1
            if file == "biggest_cluster_size.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                bcs4[nbcs] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                bcs5[nbcs] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                bcs6[nbcs] = float(line.split()[0])
                            if line.split("#")[1] == " stichovite\n":
                                bcs6stcv[nbcs] = float(line.split()[0])
                nbcs += 1
            if file == "correlation_length.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                cl4[ncl] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                cl5[ncl] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                cl6[ncl] = float(line.split()[0])
                            if line.split("#")[1] == " stichovite\n":
                                cl6stcv[ncl] = float(line.split()[0])
                ncl += 1
            if file == "order_parameter_p_infinite.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                pi4[npi] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                pi5[npi] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                pi6[npi] = float(line.split()[0])
                            if line.split("#")[1] == " stichovite\n":
                                pi6stcv[npi] = float(line.split()[0])
                npi += 1
            if file == "maximum_gyration_radius.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                rg4[nrg] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                rg5[nrg] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                rg6[nrg] = float(line.split()[0])
                            if line.split("#")[1] == " stichovite\n":
                                rg6stcv[nrg] = float(line.split()[0])
                nrg += 1
            if file == "spanning_cluster_size.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                scs4[nscs] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                scs5[nscs] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                scs6[nscs] = float(line.split()[0])
                            if line.split("#")[1] == " stichovite\n":
                                scs6stcv[nscs] = float(line.split()[0])
                nscs += 1
            if file == "percolation_1D.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                pp1D4[npp1D] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                pp1D5[npp1D] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                pp1D6[npp1D] = float(line.split()[0])
                            if line.split("#")[1] == " stichovite\n":
                                pp1D6stcv[npp1D] = float(line.split()[0])
                npp1D += 1
            if file == "percolation_2D.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                pp2D4[npp2D] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                pp2D5[npp2D] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                pp2D6[npp2D] = float(line.split()[0])
                            if line.split("#")[1] == " stichovite\n":
                                pp2D6stcv[npp2D] = float(line.split()[0])
                npp2D += 1
            if file == "percolation_3D.dat":
                with open(os.path.join(subdir, file), "r") as input:
                    for line in input:
                        if line[0] != "#":
                            if line.split("#")[1] == " 4-4\n":
                                pp3D4[npp3D] = float(line.split()[0])
                            if line.split("#")[1] == " 5-5\n":
                                pp3D5[npp3D] = float(line.split()[0])
                            if line.split("#")[1] == " 6-6\n":
                                pp3D6[npp3D] = float(line.split()[0])
                            if line.split("#")[1] == " stichovite\n":
                                pp3D6stcv[npp3D] = float(line.split()[0])
                npp3D += 1

    if path_to_pressures is not None:
        with open(path_to_pressures, "r") as inp:
            for li, l in enumerate(inp):
                Pressure.append(float(l))
        inp.close()
        Pressure = np.array(Pressure)
    else:
        Pressure = [0] * number

    if path_to_boxes is not None:
        with open(path_to_boxes, "r") as inp:
            for li, l in enumerate(inp):
                Boxe.append(float(l))
                dens = mass * 1.66054e-24 / (float(l) * 0.00000001) ** 3
                Density.append(dens)
        inp.close()
        Boxe = np.array(Boxe)
        Density = np.array(Density)
    else:
        Boxe = [0] * number
        Density = [0] * number
    try:
        with open(os.path.join(directory, "AverageClusterSize.dat"), "w") as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6", "stichovite"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], acs4[i], acs5[i], acs6[i], acs6stcv[i]
                    )
                )
    except:
        pass
    try:
        with open(os.path.join(directory, "BiggestClusterSize.dat"), "w") as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6", "stichovite"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], bcs4[i], bcs5[i], bcs6[i], bcs6stcv[i]
                    )
                )
    except:
        pass
    try:
        with open(os.path.join(directory, "SpanningClusterSize.dat"), "w") as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6", "stichovite"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], scs4[i], scs5[i], scs6[i], scs6stcv[i]
                    )
                )
    except:
        pass
    try:
        with open(os.path.join(directory, "Pinf.dat"), "w") as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6", "stichovite"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], pi4[i], pi5[i], pi6[i], pi6stcv[i]
                    )
                )
    except:
        pass
    try:
        with open(os.path.join(directory, "RadiiOfGyration.dat"), "w") as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6", "stichovite"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], rg4[i], rg5[i], rg6[i], rg6stcv[i]
                    )
                )
    except:
        pass
    try:
        with open(os.path.join(directory, "CorrelationLength.dat"), "w") as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6", "stichovite"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], cl4[i], cl5[i], cl6[i], cl6stcv[i]
                    )
                )
    except:
        pass
    try:
        with open(
            os.path.join(directory, "PercolationProbability3D.dat"), "w"
        ) as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6", "stichovite"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], pp3D4[i], pp3D5[i], pp3D6[i], pp3D6stcv[i]
                    )
                )
    except:
        pass
    try:
        with open(
            os.path.join(directory, "PercolationProbability2D.dat"), "w"
        ) as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6", "stichovite"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], pp2D4[i], pp2D5[i], pp2D6[i], pp2D6stcv[i]
                    )
                )
    except:
        pass
    try:
        with open(
            os.path.join(directory, "PercolationProbability1D.dat"), "w"
        ) as output:
            output.write(
                "#{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\t{:10s}\n".format(
                    "Boxe", "Density", "Pressure", "4-4", "5-5", "6-6", "stichovite"
                )
            )
            for i in range(len(Boxe)):
                output.write(
                    "{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\t{:6f}\n".format(
                        Boxe[i], Density[i], Pressure[i], pp1D4[i], pp1D5[i], pp1D6[i], pp1D6stcv[i]
                    )
                )
    except:
        pass
