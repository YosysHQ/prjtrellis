from collections import defaultdict
from itertools import product

from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

import isptcl

# Hint: F/Q are sinks for "driver"s, A-D are sources for "sinks".
# Bottom Fuzzing
b_overrides = dict()
for (n, r, d) in [(["R12C9_JRXDA{}_BIOLOGIC"], range(0,8), "driver"),
                  (["R12C9_JDI{}",
                    "R12C9_JIN{}_IOLOGIC"], nets.char_range("A","E"), "driver"),
                  (["R12C9_JPADDO{}",
                    "R12C9_JPADDT{}"], nets.char_range("A","E"), "driver"),
                  (["R12C9_JRXD{}A_BIOLOGIC",
                    "R12C9_JRXD{}C_BSIOLOGIC"], range(0,4), "driver"),
                  (["R12C9_JDEL{}A_BIOLOGIC",
                    "R12C9_JDEL{}C_BSIOLOGIC"], range(0,5), "sink"),
                  (["R12C9_JI{}A_BIOLOGIC",
                    "R12C9_JI{}B_IOLOGIC",
                    "R12C9_JI{}C_BSIOLOGIC",
                    "R12C9_JI{}D_IOLOGIC"], ["N", "P"], "sink"),
                  (["R12C9_JOPOS{}",
                    "R12C9_JONEG{}",
                    "R12C9_JTS{}",
                    "R12C9_JCLK{}",
                    "R12C9_JLSR{}",
                    "R12C9_JCE{}"], ["A_BIOLOGIC",
                                     "B_IOLOGIC",
                                     "C_BSIOLOGIC",
                                     "D_IOLOGIC"], "sink"),
                    (["R12C9_JSLIP{}"], ["A_BIOLOGIC",
                                         "C_BSIOLOGIC"], "sink")
              ]:
    for p in nets.net_product(n, r):
        b_overrides[p] = d

def nn_filterb(net, netnames):
    return not nets.is_cib(net)


# Left and Right are done from CIB's POV because
# there are no tiles dedicated strictly to I/O connections.
# Ignore loopback/CIBTEST nets.
l_overrides = defaultdict(lambda : str("ignore"))

# grep "R10C1_J.*" r10c1.txt | grep -v "CIBTEST" | sort | less
for (n, r, d) in [(["R10C1_JA{}",
                    "R10C1_JB{}",
                    "R10C1_JC{}",
                    "R10C1_JCLK{}",
                    "R10C1_LSR{}",
                    "R10C1_JCE{}"], range(0,4), "driver"),
                  (["R10C1_JQ{}"], range(0,4), "sink"),
                  (["R10C1_JF{}"], range(0,8), "sink")
              ]:
    for p in nets.net_product(n, r):
        l_overrides[p] = d

span1_re = re.compile(r'R\d+C\d+_[VH]01[NESWTLBR]\d{4}')
def nn_filterl(net, netnames):
    """ Match nets that are: in the tile according to Tcl, global nets, or span-1 nets that are accidentally
    left out by Tcl"""
    return net in netnames or nets.is_global(net) or span1_re.match(net)


jobs = [
        {
           "pos" : [(12, 9)],
           "cfg" : FuzzConfig(job="PIOROUTEB", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                  tiles=["PB9:PIC_B0"]),
           "nn_filter" : nn_filterb,
           "netnames_override" : b_overrides,
        },

        {
           "pos" : [(10, 1)],
           "cfg" : FuzzConfig(job="PIOROUTEL", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                  tiles=["PL10:PIC_L0"]),
           "nn_filter" : nn_filterl,
           "netnames_override" : l_overrides,
        },

        # Probably the same thing as PIC_L0 plus some additional fixed connections?
        {
           "pos" : [(11, 1)],
           "cfg" : FuzzConfig(job="PIOROUTEL", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                  tiles=["PL11:LLC0"]),
           "nn_filter" : nn_filterl,
           "netnames_override" : l_overrides,
        },

        {
            "pos" : [(10, 22)],
            "cfg" : FuzzConfig(job="PIOROUTER", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                   tiles=["PR10:PIC_R0"]),
            "nn_filter" : nn_filterl,
            "netnames_override" : l_overrides,
        },
]

def main():
    pytrellis.load_database("../../../database")
    for job in jobs:
        cfg = job["cfg"]
        cfg.setup()

        for pos in job["pos"]:
            interconnect.fuzz_interconnect(config=cfg, location=pos,
                                           netname_predicate=job["nn_filter"],
                                           netdir_override=job["netnames_override"],
                                           netname_filter_union=False,
                                           enable_span1_fix=True,
                                           bias=1)


if __name__ == "__main__":
    main()
