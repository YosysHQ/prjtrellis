import sys
from collections import defaultdict

from fuzzconfig import FuzzConfig
import pytrellis
import isptcl
import nets
import argparse
import re
import itertools
import pprint
import inspect

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

def filter_mode(args):
    span1_re = re.compile(r'R\d+C\d+_[VH]01[NESWTLBR]\d{4}')
    location = (args.row, args.col)

    def netname_predicate(net, netnames):
        """ Match nets that are: in the tile according to Tcl, global nets, or span-1 nets that are accidentally
        left out by Tcl"""
        return net in netnames or nets.machxo2.is_global(net) or span1_re.match(net)

    def arc_predicate(arc, netnames):
        return True

    def fc_predicate(arc, netnames):
        return True

    pytrellis.load_database("../../../database")

    cfg = FuzzConfig(job="FINDNETS_FILTER_R{}C{}".format(args.row, args.col), family="MachXO2", device="LCMXO2-1200HC", ncl="plc2route.ncl", tiles=[])
    cfg.setup()

    # fuzz_interconnect
    netdata = isptcl.get_wires_at_position(cfg.ncd_prf, (args.row, args.col))
    netnames = [x[0] for x in netdata]

    extra_netnames = []
    if args.s:
        for net in netnames:
            m = re.match("R(\d+)C(\d+)_V01N(\d{4})", net)
            if m:
                row = int(m.group(1))
                col = int(m.group(2))
                idn = m.group(3)
                if row == location[0] + 1 and col == location[1]:
                    fixednet = "R{}C{}_V01N{}".format(location[0] - 1, col, idn)
                    print("added {}".format(fixednet))
                    extra_netnames.append(fixednet)
        netnames = extra_netnames + netnames

    if args.f and not args.n:
        netnames = list(filter(lambda x: netname_predicate(x, netnames), netnames))

    # fuzz_interconnect_with_netnames
    arcs = isptcl.get_arcs_on_wires(cfg.ncd_prf, netnames, not args.f, defaultdict(lambda : str("mark")))

    def per_netname(net):
        assoc_arcs = arcs[net]

        if args.n:
            filt_net_pred = list(itertools.filterfalse(lambda x: netname_predicate(x[0], netnames) and netname_predicate(x[1], netnames),
                                assoc_arcs.copy()))
            assoc_arcs = list(filter(lambda x: netname_predicate(x[0], netnames) and netname_predicate(x[1], netnames),
                                assoc_arcs))
        else:
            filt_net_pred = list(itertools.filterfalse(lambda x: netname_predicate(x[0], netnames) or netname_predicate(x[1], netnames),
                                assoc_arcs.copy()))
            assoc_arcs = list(filter(lambda x: netname_predicate(x[0], netnames) or netname_predicate(x[1], netnames),
                                assoc_arcs))

        filt_arcs_pred = list(itertools.filterfalse(lambda x: arc_predicate(x, netnames), assoc_arcs.copy()))
        fuzz_arcs = list(filter(lambda x: arc_predicate(x, netnames), assoc_arcs))

        filt_fc_pred = list(itertools.filterfalse(lambda x: fc_predicate(x, netnames), fuzz_arcs.copy()))

        return (fuzz_arcs, filt_net_pred, filt_arcs_pred, filt_fc_pred)

    # Write to file, describing which nets did/didn't make the cut.
    with open("r{}c{}_filter.txt".format(args.row, args.col), "w")  as fp:
        def print_arc(arc):
            if isinstance(arc, isptcl.AmbiguousArc):
                print(str(arc), file=fp)
            else:
                print("{} --> {}".format(arc[0], arc[1]), file=fp)

        print("Args: {}".format(vars(args)), file=fp)
        print("", file=fp)

        print("Extra nets (span 1s):", file=fp)
        for net in extra_netnames:
            print("{}:".format(net), file=fp)
        print("", file=fp)

        print("Filters:", file=fp)
        print("Netname:\n{}".format(inspect.getsource(netname_predicate)), file=fp)
        print("Arc:\n{}".format(inspect.getsource(arc_predicate)), file=fp)
        print("FC:\n{}".format(inspect.getsource(fc_predicate)), file=fp)
        print("", file=fp)

        for net in netnames:
            print("{}:".format(net), file=fp)

            (fuzz, filt_net, filt_arc, filt_fc) = per_netname(net)
            print("Arcs to fuzz:", file=fp)
            for f in fuzz:
                print_arc(f)
            print("Arcs filtered by netname_predicate:", file=fp)
            for f in filt_net:
                print_arc(f)
            print("Arcs filtered by arc_predicate:", file=fp)
            for f in filt_arc:
                print_arc(f)
            print("Would be filtered by fc_predicate (if fixed connection):", file=fp)
            for f in filt_fc:
                print_arc(f)

            fp.flush()
            print("", file=fp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find which nets IspTcl returns in various ways.")
    subparsers = parser.add_subparsers()

    parser_pos = subparsers.add_parser("pos", help="Return all nets based on position.")
    parser_net = subparsers.add_parser("net", help="Return connections to one (or more) nets.")
    parser_filt = subparsers.add_parser("filter", help="Return which nets, arcs, and fixed connections will be filtered out.")

    parser_pos.add_argument("-a", action="store_true", help="Return arcs with ambiguous direction only.")
    parser_pos.add_argument("row", type=int, help="Tile row.")
    parser_pos.add_argument("col", type=int, help="Tile column.")
    parser_pos.set_defaults(func=pos_mode)

    parser_net.add_argument("nets", type=str, nargs="+", help="List of nets to find connections.")
    parser_net.set_defaults(func=net_mode)

    parser_filt.add_argument("-b", action="store_true", help="Simulate bidir (forcefully unset if -f is specified).")
    parser_filt.add_argument("-s", action="store_true", help="Enable span-1 fix.")
    parser_filt.add_argument("-n", action="store_true", help="Simulate netname_filter_union.")
    parser_filt.add_argument("-f", action="store_true", help="Simulate func_cib.")
    parser_filt.add_argument("row", type=int, help="Tile row.")
    parser_filt.add_argument("col", type=int, help="Tile column.")
    parser_filt.set_defaults(func=filter_mode)

    args = parser.parse_args()

    if len(args.__dict__) <= 1:
        # No arguments or subcommands were given.
        parser.print_help()
        parser.exit()

    args.func(args)
