import sys
from collections import defaultdict

from fuzzconfig import FuzzConfig
import pytrellis
import isptcl


def main(row, col):
    pytrellis.load_database("../../../database")

    cfg = FuzzConfig(job="FINDNETS_R{}C{}".format(row, col), family="MachXO2", device="LCMXO2-1200HC", ncl="plc2route.ncl", tiles=[])
    cfg.setup()

    netdata = isptcl.get_wires_at_position(cfg.ncd_prf, (row, col))
    netnames = [x[0] for x in netdata]
    arcs = isptcl.get_arcs_on_wires(cfg.ncd_prf, netnames, False, defaultdict(lambda : str("mark")))

    ambiguous_arcs = list()
    for (k, v) in arcs.items():
        for c in v:
            if isinstance(c, isptcl.AmbiguousArc):
                # ISPTcl always puts queried net on RHS
                ambiguous_arcs.append(c)

    with open("r{}c{}.txt".format(row, col), "w") as fp:
        for a in ambiguous_arcs:
            fp.write(str(a) + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: {} [row] [col]".format(sys.argv[0]))
    else:
        main(sys.argv[1], sys.argv[2])
