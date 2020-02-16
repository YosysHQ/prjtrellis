import sys
from collections import defaultdict

from fuzzconfig import FuzzConfig
import pytrellis
import isptcl
import argparse


def net_mode(args):
    pytrellis.load_database("../../../database")

    cfg = FuzzConfig(job="FINDNETS_NETS_{}".format(args.nets[0]), family="MachXO2", device="LCMXO2-1200HC", ncl="plc2route.ncl", tiles=[])
    cfg.setup()

    arcs = isptcl.get_arcs_on_wires(cfg.ncd_prf, args.nets, False, defaultdict(lambda : str("mark")))

    with open("{}_out.txt".format(args.nets[0]), "w") as fp:
        for (k, v) in arcs.items():
            print("{}:".format(k), file=fp)
            for c in v:
                if isinstance(c, isptcl.AmbiguousArc):
                    print(str(c), file=fp)
                else:
                    print("{} --> {}".format(c[0], c[1]), file=fp)

            fp.flush()
            print("", file=fp)

def pos_mode(args):
    pytrellis.load_database("../../../database")

    cfg = FuzzConfig(job="FINDNETS_R{}C{}".format(args.row, args.col), family="MachXO2", device="LCMXO2-1200HC", ncl="plc2route.ncl", tiles=[])
    cfg.setup()

    netdata = isptcl.get_wires_at_position(cfg.ncd_prf, (args.row, args.col))
    netnames = [x[0] for x in netdata]
    arcs = isptcl.get_arcs_on_wires(cfg.ncd_prf, netnames, False, defaultdict(lambda : str("mark")))

    with open("r{}c{}_{}out.txt".format(args.row, args.col, "a_" if args.a else ""), "w")  as fp:
        for (k, v) in arcs.items():
            print("{}:".format(k), file=fp)
            for c in v:
                if isinstance(c, isptcl.AmbiguousArc):
                    print(str(c), file=fp)
                else:
                    if not args.a:
                        print("{} --> {}".format(c[0], c[1]), file=fp)

            fp.flush()
            print("", file=fp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find which nets IspTcl returns in various ways.")
    subparsers = parser.add_subparsers()

    parser_pos = subparsers.add_parser("pos", help="Return all nets based on position.")
    parser_net = subparsers.add_parser("net", help="Return connections to one (or more) nets.")

    parser_pos.add_argument("-a", action="store_true", help="Return arcs with ambiguous direction only.")
    parser_pos.add_argument("row", type=int, help="Tile row.")
    parser_pos.add_argument("col", type=int, help="Tile column.")
    parser_pos.set_defaults(func=pos_mode)

    parser_net.add_argument("nets", type=str, nargs="+", help="List of nets to find connections.")
    parser_net.set_defaults(func=net_mode)
    args = parser.parse_args()

    if len(args.__dict__) <= 1:
        # No arguments or subcommands were given.
        parser.print_help()
        parser.exit()

    args.func(args)
