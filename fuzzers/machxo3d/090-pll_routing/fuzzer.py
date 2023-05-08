from collections import defaultdict
from fuzzconfig import FuzzConfig
import interconnect
import pytrellis
import mk_nets

jobs_route = [
    {
        "loc": (1, 2), 
        "cfg": FuzzConfig(job="PLLROUTEL", family="MachXO3D", device="LCMXO3D-9400HC", ncl="pllroute_9400.ncl",
                          tiles=["PT1:GPLL_L0"])
    },
    {
        "loc": (1, 48),
        "cfg": FuzzConfig(job="PLLROUTER", family="MachXO3D", device="LCMXO3D-9400HC", ncl="pllroute_9400R.ncl",
                          tiles=["PT49:GPLL_R0"]),
    },
]

jobs_interconnect = [
    # GPLL_L0
    {
        "loc": (1, 2), 
        "prefix" : "4300D_",
        "cfg": FuzzConfig(job="PLLROUTE_4300L", family="MachXO3D", device="LCMXO3D-4300HC", ncl="pllroute_4300.ncl",
                          tiles=["PT1:GPLL_L0"])
    },
    {
        "loc": (1, 2), 
        "prefix" : "9400D_",
        "cfg": FuzzConfig(job="PLLROUTE_9400L", family="MachXO3D", device="LCMXO3D-9400HC", ncl="pllroute_9400.ncl",
                          tiles=["PT1:GPLL_L0"])
    },
    # GPLL_R0
    {
        "loc": (1, 31), 
        "prefix" : "4300D_",
        "cfg": FuzzConfig(job="PLLROUTE_4300R", family="MachXO3D", device="LCMXO3D-4300HC", ncl="pllroute_4300R.ncl",
                          tiles=["PT32:GPLL_R0"])
    },
    {
        "loc": (1, 48), 
        "prefix" : "9400D_",
        "cfg": FuzzConfig(job="PLLROUTE_9400R", family="MachXO3D", device="LCMXO3D-9400HC", ncl="pllroute_9400R.ncl",
                          tiles=["PT49:GPLL_R0"])
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
