from collections import defaultdict

from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

import mk_nets

jobs = [
    ((6, 17), FuzzConfig(job="EBROUTE0", family="MachXO2", device="LCMXO2-1200HC", ncl="ebrroute.ncl",
                         tiles=["EBR_R6C17:EBR0", "EBR_R6C18:EBR1", "EBR_R6C19:EBR2"])),

    ((6, 1), FuzzConfig(job="EBROUTE0", family="MachXO2", device="LCMXO2-1200HC", ncl="ebrroute.ncl",
                        tiles=["EBR_R6C1:EBR0_END"])),
]


def main():
    pytrellis.load_database("../../../database")
    for job in jobs:
        loc, cfg = job
        cfg.setup()

        ebr_nets = mk_nets.ebr_conns(loc)
        ebr_list = [ebr[0] for ebr in ebr_nets]
        override_dict = {ebr[0]: ebr[1] for ebr in ebr_nets}

        interconnect.fuzz_interconnect_with_netnames(config=cfg,      
                                                     netnames=ebr_list,
                                                     netname_filter_union=False,
                                                     bidir=True,
                                                     netdir_override=override_dict)


if __name__ == "__main__":
    main()
