from collections import defaultdict
from itertools import product

from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

import isptcl

# jobs = [
#     {
#         "pos": [(47, 0), (48, 0), (49, 0)],
#         "cfg": FuzzConfig(job="PIOROUTEL", family="ECP5", device="LFE5U-45F", ncl="pioroute.ncl",
#                           tiles=["MIB_R47C0:PICL0", "MIB_R48C0:PICL1", "MIB_R49C0:PICL2"])
#     },
#     {
#         "pos": [(47, 90), (48, 90), (49, 90)],
#         "cfg": FuzzConfig(job="PIOROUTER", family="ECP5", device="LFE5U-45F", ncl="pioroute.ncl",
#                           tiles=["MIB_R47C90:PICR0", "MIB_R48C90:PICR1", "MIB_R49C90:PICR2"])
#     },
#     {
#         "pos": [(0, 22), (1, 23), (0, 22), (1, 23)],
#         "cfg": FuzzConfig(job="PIOROUTET", family="ECP5", device="LFE5U-45F", ncl="pioroute.ncl",
#                           tiles=["MIB_R0C22:PIOT0", "MIB_R0C23:PIOT1", "MIB_R1C22:PICT0", "MIB_R1C23:PICT1"])
#     },
#     {
#         "pos": [(71, 11), (71, 12), (70, 11), (70, 12)],
#         "cfg": FuzzConfig(job="PIOROUTET", family="ECP5", device="LFE5U-45F", ncl="pioroute.ncl",
#                           tiles=["MIB_R71C11:PICB0", "MIB_R71C12:PICB1"])
#     }
# ]


# Hint: F/Q are sinks for "driver"s, A-D are sources for "sinks".
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
                                         "C_BSIOLOGIC"], "sink"),
              ]:
    for p in nets.net_product(n, r):
        b_overrides[p] = d

jobs = [
        {
            "pos" : [(12, 9)],
            "cfg" : FuzzConfig(job="PIOROUTEB", family="MachXO2", device="LCMXO2-1200HC", ncl="pioroute.ncl",
                                   tiles=["PB9:PIC_B0"]),
            "netnames" : nets.net_product(["R12C9_JDI{}",],
                                      nets.char_range("A", "E")),
            "netnames_override" : b_overrides,
            "concat" : nets.net_product(["R12C9_JPADDT{}", "R12C9_JPADDO{}"],
                                       nets.char_range("A", "E"))
        }
]

def main():
    pytrellis.load_database("../../../database")
    for job in jobs:
        cfg = job["cfg"]
        cfg.setup()

        def nn_filter(net, netnames):
            return not nets.is_cib(net)
        orig_tiles = cfg.tiles
        for pos in job["pos"]:
            # Put fixed connections in the most appropriate tile
            # target_tile = None
            # for tile in orig_tiles:
            #     if "R{}C{}".format(pos[0], pos[1]) in tile:
            #         target_tile = tile
            #         break
            # if target_tile is not None:
            #     cfg.tiles = [target_tile] + [_ for _ in orig_tiles if _ != orig_tiles]
            # else:
            #     cfg.tiles = orig_tiles

            # Test fuzzers follow below

            # First fuzzing attempt.
            interconnect.fuzz_interconnect(config=cfg, location=pos,
                                           netname_predicate=nn_filter,
                                           netdir_override=job["netnames_override"],
                                           netname_filter_union=False,
                                           bias=1)

            # "R12C9_DI{}_BIOLOGIC"
            # TODO: Check that override message is returning the LEFT hand side
            # on error in 040-center-cib.
            # interconnect.fuzz_interconnect_with_netnames(config=cfg,
            #                                netnames=job["netnames"],
            #                                netname_predicate=nn_filter,
            #                                netdir_override=job["netnames_override"],
            #                                netname_filter_union=False,
            #                                bidir=True,
            #                                bias=1)
            #
            #
            # # Concatenated nets.
            # interconnect.fuzz_interconnect_with_netnames(config=cfg,
            #                                  netnames=job["concat"],
            #                                  netname_filter_union=False,
            #                                  netdir_override=defaultdict(lambda : str("sink")),
            #                                  bidir=True,
            #                                  bias=1)


if __name__ == "__main__":
    main()
