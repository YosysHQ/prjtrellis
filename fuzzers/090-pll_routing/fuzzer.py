from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

jobs = [
    ((4, 1), "45K_", FuzzConfig(job="PLLROUTE0", family="ECP5", device="LFE5U-45F", ncl="pllroute.ncl",
                          tiles=["MIB_R4C0:PLL0_UL", "MIB_R5C0:PLL1_UL"])),

]


def main():
    pytrellis.load_database("../../database")
    for job in jobs:
        loc, prefix, cfg = job
        cfg.setup()

        def nn_filter(net, netnames):
            return "PLL" in net or "CLKFB" in net or "CLKINT" in net or "REFCLK" in net

        interconnect.fuzz_interconnect(config=cfg, location=loc,
                                       netname_predicate=nn_filter,
                                       netname_filter_union=False,
                                       func_cib=True,
                                       nonlocal_prefix=prefix)


if __name__ == "__main__":
    main()
