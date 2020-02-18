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
def nn_filterl(net, netnames):
    """ Match nets that are: in the tile according to Tcl, global nets, or span-1 nets that are accidentally
    left out by Tcl"""
    return net in netnames or nets.is_global(net) or span1_re.match(net)

def nn_filterb(net, netnames):
    return net in netnames or nets.is_global(net) or span1_re.match(net)

jobs = [
        {
           "pos" : [(12, 11)],
           "cfg" : FuzzConfig(job="PIOROUTEB", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                  tiles=["PB11:PIC_B0"]),
           "nn_filter" : nn_filterb,
           "override_id" : "b",
           "missing_nets" : []
        },
        {
           "pos" : [(11, 11)],
           "cfg" : FuzzConfig(job="PIOROUTEB_CIB", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                  tiles=["CIB_R11C11:CIB_PIC_B0"]),
           "nn_filter" : nn_filterb,
           "override_id" : "b_cib",
           # A bug in the span1 fix prevents span1 nets from being included.
           # Just fuzz manually for now.
           "missing_nets" : ["R10C11_V01N0001", "R10C11_V01N0101"]
        },
        {
           "pos" : [(10, 1)],
           "cfg" : FuzzConfig(job="PIOROUTEL", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                  tiles=["PL10:PIC_L0"]),
           "nn_filter" : nn_filterl,
           "override_id" : "l",
           "missing_nets" : []
        },

        # Probably the same thing as PIC_L0 plus some additional fixed connections?
        {
           "pos" : [(11, 1)],
           "cfg" : FuzzConfig(job="PIOROUTEL", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                  tiles=["PL11:LLC0"]),
           "nn_filter" : nn_filterl,
           "override_id" : "llc",
           "missing_nets" : []
        },

        {
            "pos" : [(10, 22)],
            "cfg" : FuzzConfig(job="PIOROUTER", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                   tiles=["PR10:PIC_R0"]),
            "nn_filter" : nn_filterl,
            "override_id" : "r",
            "missing_nets" : []
        },
]

def main(args):
    pytrellis.load_database("../../../database")
    for job in [jobs[i] for i in args.ids]:
        cfg = job["cfg"]
        cfg.setup()

    for pos in job["pos"]:
        interconnect.fuzz_interconnect(config=cfg, location=pos,
                                       netname_predicate=job["nn_filter"],
                                       netdir_override=mk_nets.overrides[job["override_id"]],
                                       netname_filter_union=False,
                                       enable_span1_fix=True,
                                       bias=1)

        if job["missing_nets"]:
            interconnect.fuzz_interconnect_with_netnames(config=cfg,
                                                         netnames=job["missing_nets"],
                                                         netname_filter_union=False,
                                                         bidir=True,
                                                         netdir_override=defaultdict(lambda : str("sink")),
                                                         bias=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CIB_EBRn Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
