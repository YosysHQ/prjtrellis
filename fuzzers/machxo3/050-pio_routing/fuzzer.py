from collections import defaultdict
from itertools import product

from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re
import argparse

import isptcl
import mk_nets

span1_re = re.compile(r'R\d+C\d+_[VH]01[NESWTLBR]\d{4}')
jofx_re = re.compile(r'R\d+C\d+_JOFX\d')
def nn_filter(net, netnames):
    """ Match nets that are: in the tile according to Tcl, global nets, or span-1 nets that are accidentally
    left out by Tcl"""
    return net in netnames or nets.machxo2.is_global(net) or span1_re.match(net)

# JOFX source connections are conjectured to not go to anything.
# Also ignore edge connections.
# TODO: We should probably ignore KEEP connections too, but right now am unsure.
def fc_filter(arc, netnames):
    return not jofx_re.match(arc[0]) and not (nets.general_routing_re.match(arc[0]) and nets.general_routing_re.match(arc[1]))

# Bank of None means that the I/O connections are in another tile.
jobs = [
        {
           "pos" : (27, 12),
           "cfg" : FuzzConfig(job="PIOROUTEB", family="MachXO3LF", device="LCMXO3LF-6900C", ncl="pioroute.ncl",
                                  tiles=["PB12:PIC_B0"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "B",
        },
        {
           "pos" : (27, 11),
           "cfg" : FuzzConfig(job="PIOROUTEB_CIB", family="MachXO3LF", device="LCMXO3LF-6900C", ncl="pioroute.ncl",
                                  tiles=["CIB_R11C11:CIB_PIC_B0"]),
            # A bug in the span1 fix prevents span1 nets from being included.
            # Just fuzz manually for now.
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : None,
        },
        {
           "pos" : (10, 1),
           "cfg" : FuzzConfig(job="PIOROUTEL", family="MachXO3LF", device="LCMXO3LF-6900C", ncl="pioroute.ncl",
                                  tiles=["PL10:PIC_L2"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "L"
        },

        # Probably the same thing as PIC_L0 plus some additional fixed connections?
        {
           "pos" : (26, 1),
           "cfg" : FuzzConfig(job="PIOROUTELLC2", family="MachXO3LF", device="LCMXO3LF-6900C", ncl="pioroute.ncl",
                                  tiles=["PL26:LLC2"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "L"
        },

        # 4
        {
           "pos" : (25, 41),
           "cfg" : FuzzConfig(job="PIOROUTER", family="MachXO3LF", device="LCMXO3LF-6900C", ncl="pioroute.ncl",
                                   tiles=["PR25:PIC_R1"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "R"
        },
]

def main(args):
    pytrellis.load_database("../../../database")
    for job in [jobs[i] for i in args.ids]:
        cfg = job["cfg"]
        cfg.setup()

        if args.i:
            # Fuzz basic routing, ignore fixed connections to/from I/O pads.
            interconnect.fuzz_interconnect(config=cfg, location=job["pos"],
                                           netname_predicate=job["nn_filter"],
                                           netdir_override=defaultdict(lambda : str("ignore")),
                                           fc_predicate=fc_filter,
                                           netname_filter_union=False,
                                           enable_span1_fix=True)

        if args.m and job["missing_nets"]:
            interconnect.fuzz_interconnect_with_netnames(config=cfg,
                                                         netnames=job["missing_nets"],
                                                         fc_predicate=fc_filter,
                                                         netname_filter_union=False,
                                                         bidir=True,
                                                         netdir_override=defaultdict(lambda : str("ignore")))


        if args.p and job["bank"]:
            # I/O connections in the left/right tiles exist as-if a column "0"
            # or one past maximum is physically present.
            if job["bank"].startswith("R"):
                ab_only = job["bank"].endswith("S")
                io_nets = mk_nets.io_conns((job["pos"][0], job["pos"][1] + 1), job["bank"], ab_only)
            elif job["bank"].startswith("L"):
                ab_only = job["bank"].endswith("S")
                io_nets = mk_nets.io_conns((job["pos"][0], job["pos"][1] - 1), job["bank"], ab_only)
            else:
                io_nets = mk_nets.io_conns((job["pos"][0], job["pos"][1]), job["bank"])

            io_list = [io[0] for io in io_nets]
            override_dict = {io[0]: io[1] for io in io_nets}
            print(override_dict)

            interconnect.fuzz_interconnect_with_netnames(config=cfg,
                                                         netnames=io_list,
                                                         fc_predicate=fc_filter,
                                                         netname_filter_union=False,
                                                         bidir=True,
                                                         netdir_override=override_dict)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PIO Routing Fuzzer.")
    parser.add_argument("-i", action="store_true", help="Fuzz interconnect.")
    parser.add_argument("-m", action="store_true", help="Fuzz missing nets.")
    parser.add_argument("-p", action="store_true", help="Fuzz I/O pad connections.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
