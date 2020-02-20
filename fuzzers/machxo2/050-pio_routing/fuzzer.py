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
    return net in netnames or nets.is_global(net) or span1_re.match(net)

# JOFX source connections are conjectured to not go to anything.
def fc_filter(arc, netnames):
    return not jofx_re.match(arc[0])

# Bank of None means that the I/O connections are in another tile.
jobs = [
        {
           "pos" : [(12, 11)],
           "cfg" : FuzzConfig(job="PIOROUTEB", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                  tiles=["PB11:PIC_B0"]),
           "missing_nets" : None,
           "bank" : "B",
        },
        {
           "pos" : [(11, 11)],
           "cfg" : FuzzConfig(job="PIOROUTEB_CIB", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                  tiles=["CIB_R11C11:CIB_PIC_B0"]),
            # A bug in the span1 fix prevents span1 nets from being included.
            # Just fuzz manually for now.
           "missing_nets" : ["R10C11_V01N0001", "R10C11_V01N0101"],
           "bank" : None,
        },
        {
           "pos" : [(10, 1)],
           "cfg" : FuzzConfig(job="PIOROUTEL", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                  tiles=["PL10:PIC_L0"]),
           "missing_nets" : None,
           "bank" : "L"
        },

        # Probably the same thing as PIC_L0 plus some additional fixed connections?
        {
           "pos" : [(11, 1)],
           "cfg" : FuzzConfig(job="PIOROUTELLC0", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                  tiles=["PL11:LLC0"]),
           "missing_nets" : None,
           "bank" : "L"
        },
        {
           "pos" : [(10, 22)],
           "cfg" : FuzzConfig(job="PIOROUTER", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                   tiles=["PR10:PIC_R0"]),
           "missing_nets" : None,
           "bank" : "R"
        },
        {
           "pos" : [(0, 12)],
           "cfg" : FuzzConfig(job="PIOROUTET", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                  tiles=["PT12:PIC_T0"]),
           "missing_nets" : None,
           "bank" : "T",
        },
        {
           "pos" : [(1, 12)],
           "cfg" : FuzzConfig(job="PIOROUTET_CIB", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                  tiles=["CIB_R1C12:CIB_PIC_T0"]),
           "missing_nets" : None,
           "bank" : None,
        },
]

def main(args):
    pytrellis.load_database("../../../database")
    for job in [jobs[i] for i in args.ids]:
        cfg = job["cfg"]
        cfg.setup()

        if args.i:
            # Fuzz basic routing, ignore fixed connections to/from I/O pads.
            interconnect.fuzz_interconnect(config=cfg, location=pos,
                                           netname_predicate=nn_filter,
                                           netdir_override=defaultdict(lambda : str("ignore")),
                                           fc_predicate=fc_filter,
                                           netname_filter_union=False,
                                           enable_span1_fix=True,
                                           bias=1)

        if args.m and job["missing_nets"]:
            interconnect.fuzz_interconnect_with_netnames(config=cfg,
                                                         netnames=job["missing_nets"],
                                                         fc_predicate=fc_filter,
                                                         netname_filter_union=False,
                                                         bidir=True,
                                                         netdir_override=mk_nets.overrides[job["mknets_id"]],
                                                         bias=1)


        if args.p and job["bank"]:
            # I/O connections in the left/right tiles exist as-if a column "0"
            # or one past maximum is physically present.
            if job["bank"] == "R":
                io_nets = mk_nets.io_conns((job["pos"][0][0], job["pos"][0][1] + 1), job["bank"])
            elif job["bank"] == "L":
                io_nets = mk_nets.io_conns((job["pos"][0][0], job["pos"][0][1] - 1), job["bank"])
            else:
                io_nets = mk_nets.io_conns(job["pos"][0], job["bank"])

            io_list = [io[0] for io in io_nets]
            override_dict = {io[0]: io[1] for io in io_nets}
            print(override_dict)

            interconnect.fuzz_interconnect_with_netnames(config=cfg,
                                                         netnames=io_list,
                                                         fc_predicate=fc_filter,
                                                         netname_filter_union=False,
                                                         bidir=True,
                                                         netdir_override=override_dict,
                                                         bias=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CIB_EBRn Fuzzer.")
    parser.add_argument("-i", action="store_true", help="Fuzz interconnect.")
    parser.add_argument("-m", action="store_true", help="Fuzz missing nets.")
    parser.add_argument("-p", action="store_true", help="Fuzz I/O pad connections.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
