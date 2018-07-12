from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

jobs = [
    ((4, 1), "45K_", FuzzConfig(job="PLLROUTE0", family="ECP5", device="LFE5U-45F", ncl="pllroute.ncl",
                          tiles=["MIB_R4C0:PLL0_UL", "MIB_R5C0:PLL1_UL"])),
    ((70, 2), "45K_", FuzzConfig(job="PLLROUTE1", family="ECP5", device="LFE5U-45F", ncl="pllroute.ncl",
                                tiles=["MIB_R71C2:PLL0_LL", "MIB_R71C3:BANKREF8"])),
    ((70, 88), "45K_", FuzzConfig(job="PLLROUTE2", family="ECP5", device="LFE5U-45F", ncl="pllroute.ncl",
                                 tiles=["MIB_R71C88:PLL0_LR", "MIB_R71C87:PLL1_LR"])),
    ((4, 89), "45K_", FuzzConfig(job="PLLROUTE3", family="ECP5", device="LFE5U-45F", ncl="pllroute.ncl",
                                  tiles=["MIB_R4C90:PLL0_UR", "MIB_R5C90:PLL1_UR"])),
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
