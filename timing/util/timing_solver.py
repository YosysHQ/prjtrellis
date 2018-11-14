from scipy import optimize
from scipy.sparse import linalg
import numpy
import parse_sdf
import design_pip_classes
import pip_classes
import sys
import math
import json


def solve_pip_delays(ncl, sdf, debug=False):
    path_pip_classes, wire_fanout = design_pip_classes.get_equations(ncl)
    sdf_data = parse_sdf.parse_sdf_file(sdf)
    top_ic = None
    for cell in sdf_data.cells:
        if len(sdf_data.cells[cell].interconnect) != 0:
            top_ic = sdf_data.cells[cell].interconnect
            break
    assert top_ic is not None
    variables = {}
    for path in sorted(path_pip_classes.values()):
        for wire, pipclass in path:
            if (pipclass, "delay") not in variables and not pip_classes.force_zero_delay_pip(pipclass):
                vid = len(variables)
                variables[pipclass, "delay"] = vid
            if not pip_classes.force_zero_fanout_pip(pipclass):
                if (pipclass, "fanout") not in variables:
                    vid = len(variables)
                    variables[pipclass, "fanout"] = vid
    kfid = len(variables)
    data = {}
    corners = "min", "typ", "max"
    i = 0
    A = numpy.zeros((len(path_pip_classes), len(variables)))
    for arc, path in sorted(path_pip_classes.items()):
        for wire, pipclass in path:
            if not pip_classes.force_zero_delay_pip(pipclass):
                A[i, variables[pipclass, "delay"]] += 1
            if not pip_classes.force_zero_fanout_pip(pipclass):
                A[i, variables[pipclass, "fanout"]] += wire_fanout[wire, pipclass]
            if pipclass not in data:
                data[pipclass] = {
                    "delay": [0, 0, 0],
                    "fanout": [0, 0, 0],
                }
        i += 1

    for corner in corners:
        b = numpy.zeros((len(path_pip_classes), ))
        i = 0
        for arc, path in sorted(path_pip_classes.items()):
            src, dest = arc
            srcname = "{}/{}".format(src[0].replace('/', '\\/').replace('.', '\\.'), src[1])
            destname = "{}/{}".format(dest[0].replace('/', '\\/').replace('.', '\\.'), dest[1])
            b[i] = getattr(top_ic[srcname, destname].rising, corner + "v")
            i += 1
        print("Starting least squares solver!")
        x, rnorm = optimize.nnls(A, b)
        for var, j in sorted(variables.items()):
            pipclass, vartype = var
            data[pipclass][vartype][corners.index(corner)] = x[j]
    if debug:
        error = numpy.matmul(A, x) - b
        i = 0
        worst = 0
        sqsum = 0
        for arc, path in sorted(path_pip_classes.items()):
            src, dest = arc
            rel_error = error[i] / b[i]
            print("error {}.{} -> {}.{} = {:.01f} ps ({:.01f} %)".format(src[0], src[1], dest[0], dest[1], error[i], rel_error * 100))
            worst = max(worst, abs(error[i]))
            sqsum += error[i]**2
            i = i + 1
        with open("error.csv", "w") as f:
            print("actual, percent", file=f)
            for i in range(len(path_pip_classes)):
                rel_error = error[i] / b[i]
                print("{}, {}".format(b[i], rel_error * 100), file=f)
        for var, j in sorted(variables.items()):
            print("{}_{} = {:.01f} ps".format(var[0], var[1], x[j]))
        print("Error: {:.01f} ps max, {:.01f} ps RMS".format(worst, math.sqrt(sqsum / len(path_pip_classes))))
    return data

def main():
    data = solve_pip_delays(sys.argv[1], sys.argv[2], debug=True)
    with open("out.json", "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)

if __name__ == "__main__":
    main()
