from scipy import optimize
from scipy.sparse import linalg
import numpy
import parse_sdf
import design_pip_classes
import sys
import math


def solve_pip_delays(ncl, sdf):
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
            if pipclass + "_delay" not in variables:
                vid = len(variables)
                variables[pipclass + "_delay"] = vid
            if pipclass + "_fanout" not in variables:
                vid = len(variables)
                variables[pipclass + "_fanout"] = vid
    kfid = len(variables)
    variables["k_fanout"] = kfid
    A = numpy.zeros((len(path_pip_classes), len(variables)))
    b = numpy.zeros((len(path_pip_classes), ))
    i = 0
    for arc, path in sorted(path_pip_classes.items()):
        src, dest = arc
        for wire, pipclass in path:
            A[i, variables[pipclass + "_delay"]] += 1
            # fixme
            if pipclass != "slice_internal":
                A[i, variables[pipclass + "_fanout"]] += wire_fanout[wire, pipclass]

        srcname = "{}/{}".format(src[0].replace('/', '\\/').replace('.', '\\.'), src[1])
        destname = "{}/{}".format(dest[0].replace('/', '\\/').replace('.', '\\.'), dest[1])
        b[i] = top_ic[srcname, destname].rising.maxv
        i += 1
    print("Starting least squares solver!")
    #print(A)
    #print(b)
    x, rnorm = optimize.nnls(A, b)
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
        print("{} = {:.01f} ps".format(var, x[j]))
    print("Error: {:.01f} ps max, {:.01f} ps RMS".format(worst, math.sqrt(sqsum / len(path_pip_classes))))

def main():
    solve_pip_delays(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
