from scipy import sparse
from scipy.sparse import linalg
import numpy
import parse_sdf
import design_pip_classes
import sys

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
            #if pipclass + "_fanout" not in variables:
            #    vid = len(variables)
            #    variables[pipclass + "_fanout"] = vid
    A = sparse.lil_matrix((len(path_pip_classes), len(variables)))
    b = []
    i = 0
    for arc, path in sorted(path_pip_classes.items()):
        src, dest = arc
        for wire, pipclass in path:
            A[i, variables[pipclass + "_delay"]] = 1
            # fixme
            # A[i, variables[pipclass + "_fanout"]] = wire_fanout[wire, pipclass]
        srcname = "{}/{}".format(src[0].replace('/', '\\/').replace('.', '\\.'), src[1])
        destname = "{}/{}".format(dest[0].replace('/', '\\/').replace('.', '\\.'), dest[1])
        b.append(top_ic[srcname, destname].rising.maxv)
        i += 1
    print("Starting least squares solver!")
    #print(A)
    #print(b)
    x, istop, itn, normr = linalg.lsqr(A, b)[:4]
    for var, j in sorted(variables.items()):
        print("{} = {}".format(var, x[j]))


def main():
    solve_pip_delays(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
