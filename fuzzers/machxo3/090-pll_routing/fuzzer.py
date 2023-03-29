from collections import defaultdict
from fuzzconfig import FuzzConfig
import interconnect
import pytrellis

jobs = [
    ((1, 2), FuzzConfig(job="PLLROUTE0", family="MachXO3", device="LCMXO3LF-1300E", ncl="pllroute_1300.ncl",
                          tiles=["PT1:GPLL_L0"])),


    ((1, 40), FuzzConfig(job="PLLROUTE0", family="MachXO3", device="LCMXO3LF-6900C", ncl="pllroute_6900.ncl",
                          tiles=["PT41:GPLL_R0"])),

]


def main():
    pytrellis.load_database("../../../database")
    for job in jobs:
        loc,cfg = job
        cfg.setup()
        
        def nn_filter(net, netnames):
            return "PLL" in net or "CLKFB" in net or "REFCLK" in net


        interconnect.fuzz_interconnect(config=cfg, location=loc,
                                        netname_predicate=nn_filter,
                                        netname_filter_union=True,
                                        netdir_override=defaultdict(lambda : str("ignore")),
                                        enable_span1_fix=True)


if __name__ == "__main__":
    main()
