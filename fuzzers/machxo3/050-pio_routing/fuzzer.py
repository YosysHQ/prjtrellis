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
           "pos" : (12, 11),
           "cfg" : FuzzConfig(job="PIOROUTEB", family="MachXO3", device="LCMXO3LF-1300E", ncl="pioroute_1300.ncl",
                                  tiles=["PB11:PIC_B0"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "B",
        },
        {
           "pos" : (10, 1),
           "cfg" : FuzzConfig(job="PIOROUTEL", family="MachXO3", device="LCMXO3LF-1300E", ncl="pioroute_1300.ncl",
                                  tiles=["PL10:PIC_L0"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "L"
        },

        # Probably the same thing as PIC_L0 plus some additional fixed connections?
        {
           "pos" : (11, 1),
           "cfg" : FuzzConfig(job="PIOROUTELLC0", family="MachXO3", device="LCMXO3LF-1300E", ncl="pioroute_1300.ncl",
                                  tiles=["PL11:LLC0"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "L"
        },

        {
           "pos" : (10, 22),
           "cfg" : FuzzConfig(job="PIOROUTER", family="MachXO3", device="LCMXO3LF-1300E", ncl="pioroute_1300.ncl",
                                   tiles=["PR10:PIC_R0"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "R"
        },
        # 4
        {
           "pos" : (0, 12),
           "cfg" : FuzzConfig(job="PIOROUTET", family="MachXO3", device="LCMXO3LF-1300E", ncl="pioroute_1300.ncl",
                                  tiles=["PT12:PIC_T0"]),
           "missing_nets" : None,
           "nn_filter" : lambda x, nets: x.startswith("R0C12"),
           "bank" : "T",
        },

        {
           "pos" : (9, 1),
           "cfg" : FuzzConfig(job="PIOROUTELS0", family="MachXO3", device="LCMXO3LF-1300E", ncl="pioroute_1300.ncl",
                                  tiles=["PL9:PIC_LS0"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "LS",
        },

        {
           "pos" : (3, 22),
           "cfg" : FuzzConfig(job="PIOROUTERS0", family="MachXO3", device="LCMXO3LF-1300E", ncl="pioroute_1300.ncl",
                                  tiles=["PR3:PIC_RS0"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "RS",
        },

        {
           "pos" : (10, 1),
           "cfg" : FuzzConfig(job="PIOROUTEL", family="MachXO3", device="LCMXO3LF-6900C", ncl="pioroute_6900.ncl",
                                  tiles=["PL10:PIC_L2"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "L"
        },

        # 8
        # Probably the same thing as PIC_L2 plus some additional fixed connections?
        {
           "pos" : (26, 1),
           "cfg" : FuzzConfig(job="PIOROUTELLC2", family="MachXO3", device="LCMXO3LF-6900C", ncl="pioroute_6900.ncl",
                                  tiles=["PL26:LLC2"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "L"
        },

        {
           "pos" : (25, 41),
           "cfg" : FuzzConfig(job="PIOROUTER", family="MachXO3", device="LCMXO3LF-6900C", ncl="pioroute_6900.ncl",
                                   tiles=["PR25:PIC_R1"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "R"
        },

        {
           "pos" : (10, 1),
           "cfg" : FuzzConfig(job="PIOROUTEL", family="MachXO3", device="LCMXO3LF-2100C", ncl="pioroute_2100.ncl",
                                  tiles=["PL10:PIC_L3"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "L"
        },

        {
           "pos" : (14, 1),
           "cfg" : FuzzConfig(job="PIOROUTEL", family="MachXO3", device="LCMXO3LF-4300C", ncl="pioroute_4300.ncl",
                                  tiles=["PL14:PIC_L1"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "L"
        },

        # 12
        {
           "pos" : (21, 1),
           "cfg" : FuzzConfig(job="PIOROUTELLC1", family="MachXO3", device="LCMXO3LF-4300C", ncl="pioroute_4300.ncl",
                                  tiles=["PL21:LLC1"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "L"
        },

        {
           "pos" : (11, 22),
           "cfg" : FuzzConfig(job="PIOROUTELRC0", family="MachXO3", device="LCMXO3LF-1300E", ncl="pioroute_1300.ncl",
                                  tiles=["PR11:LRC0"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "R"
        },

        {
           "pos" : (21, 32),
           "cfg" : FuzzConfig(job="PIOROUTELRC1", family="MachXO3", device="LCMXO3LF-4300C", ncl="pioroute_4300.ncl",
                                  tiles=["PR21:LRC1"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "R"
        },

        {
           "pos" : (14, 26),
           "cfg" : FuzzConfig(job="PIOROUTELRC1PIC2", family="MachXO3", device="LCMXO3LF-2100C", ncl="pioroute_2100.ncl",
                                  tiles=["PR14:LRC1PIC2"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "R"
        },
        #16
        {
           "pos" : (1, 1),
           "cfg" : FuzzConfig(job="PIOROUTEULC1", family="MachXO3", device="LCMXO3LF-4300C", ncl="pioroute_4300.ncl",
                                  tiles=["PL1:ULC1"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "L"
        },
        {
           "pos" : (1, 1),
           "cfg" : FuzzConfig(job="PIOROUTEULC2", family="MachXO3", device="LCMXO3LF-6900C", ncl="pioroute_6900.ncl",
                                  tiles=["PL1:ULC2"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "L"
        },
        {
           "pos" : (1, 1),
           "cfg" : FuzzConfig(job="PIOROUTEULC3PIC", family="MachXO3", device="LCMXO3LF-2100C", ncl="pioroute_2100.ncl",
                                  tiles=["PL1:ULC3PIC"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "L"
        },
        {
           "pos" : (1, 26),
           "cfg" : FuzzConfig(job="PIOROUTEURC1PIC", family="MachXO3", device="LCMXO3LF-2100C", ncl="pioroute_2100.ncl",
                                  tiles=["PR1:URC1PIC"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "R"
        },
        #20
        {
           "pos" : (30, 1),
           "cfg" : FuzzConfig(job="PIOROUTELLC0PIC_VREF3", family="MachXO3", device="LCMXO3LF-9400C", ncl="pioroute_9400.ncl",
                                  tiles=["PL30:LLC0PIC_VREF3"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "L"
        },
        {
           "pos" : (14, 1),
           "cfg" : FuzzConfig(job="PIOROUTELLC1PIC_VREF3", family="MachXO3", device="LCMXO3LF-2100C", ncl="pioroute_2100.ncl",
                                  tiles=["PL14:LLC3PIC_VREF3"]),
           "missing_nets" : None,
           "nn_filter": nn_filter,
           "bank" : "L"
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
