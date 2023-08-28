from collections import defaultdict
from fuzzconfig import FuzzConfig
import interconnect
import pytrellis
import mk_nets

jobs_route = [
    {
        "loc": (1, 2), 
        "cfg": FuzzConfig(job="PLLROUTE0", family="MachXO2", device="LCMXO2-1200HC", ncl="pllroute_1200.ncl",
                          tiles=["PT1:GPLL_L0"])
    },
    {
        "loc": (1, 40),
        "cfg": FuzzConfig(job="PLLROUTE0", family="MachXO2", device="LCMXO2-7000HC", ncl="pllroute_7000R.ncl",
                          tiles=["PT41:GPLL_R0"]),
    },
]

jobs_interconnect = [
    # GPLL_L0
    {
        "loc": (1, 2), 
        "prefix" : "1200_",
        "cfg": FuzzConfig(job="PLLROUTE0", family="MachXO2", device="LCMXO2-1200HC", ncl="pllroute_1200.ncl",
                          tiles=["PT1:GPLL_L0"])
    },
    {
        "loc": (1, 2), 
        "prefix" : "2000_",
        "cfg": FuzzConfig(job="PLLROUTE0", family="MachXO2", device="LCMXO2-2000HC", ncl="pllroute_2000.ncl",
                          tiles=["PT1:GPLL_L0"])
    },
    {
        "loc": (1, 2), 
        "prefix" : "4000_",
        "cfg": FuzzConfig(job="PLLROUTE0", family="MachXO2", device="LCMXO2-4000HC", ncl="pllroute_4000.ncl",
                          tiles=["PT1:GPLL_L0"])
    },
    {
        "loc": (1, 2), 
        "prefix" : "7000_",
        "cfg": FuzzConfig(job="PLLROUTE0", family="MachXO2", device="LCMXO2-7000HC", ncl="pllroute_7000.ncl",
                          tiles=["PT1:GPLL_L0"])
    },
    # GPLL_R0
    {
        "loc": (1, 31), 
        "prefix" : "4000_",
        "cfg": FuzzConfig(job="PLLROUTE0", family="MachXO2", device="LCMXO2-4000HC", ncl="pllroute_4000R.ncl",
                          tiles=["PT32:GPLL_R0"])
    },
    {
        "loc": (1, 40), 
        "prefix" : "7000_",
        "cfg": FuzzConfig(job="PLLROUTE0", family="MachXO2", device="LCMXO2-7000HC", ncl="pllroute_7000R.ncl",
                          tiles=["PT41:GPLL_R0"])
    },
]

def main():
    pytrellis.load_database("../../../database")
    for job in jobs_route:
        cfg = job["cfg"]
        cfg.setup()
        
        def nn_filter(net, netnames):
            return "PLL" in net or "CLKFB" in net or "CLKINTFB" in net or "REFCLK" in net or "TECLK" in net


        interconnect.fuzz_interconnect(config=cfg, location=job["loc"],
                                        netname_predicate=nn_filter,
                                        netname_filter_union=True,
                                        netdir_override=defaultdict(lambda : str("ignore")),
                                        enable_span1_fix=True)


    for job in jobs_interconnect:
        cfg = job["cfg"]
        cfg.setup()
        pll_nets = mk_nets.pll_nets(job["loc"])
        pll_list = [pll[0] for pll in pll_nets]
        override_dict = {pll[0]: pll[1] for pll in pll_nets}

        interconnect.fuzz_interconnect_with_netnames(config=cfg,      
                                                     netnames=pll_list,
                                                     netname_filter_union=False,
                                                     nonlocal_prefix=job["prefix"],
                                                     bidir=True,
                                                     netdir_override=override_dict)


if __name__ == "__main__":
    main()
