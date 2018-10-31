from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

jobs = [
    ((4, 1), "45K_", FuzzConfig(job="PLLROUTE0", family="ECP5", device="LFE5U-45F", ncl="pllroute.ncl",
                          tiles=["MIB_R4C0:PLL0_UL", "MIB_R5C0:PLL1_UL", "CIB_R4C1:CIB_PLL0", "CIB_R5C1:CIB_PLL1"])),
    ((70, 2), "45K_", FuzzConfig(job="PLLROUTE1", family="ECP5", device="LFE5U-45F", ncl="pllroute.ncl",
                                tiles=["MIB_R71C2:PLL0_LL", "MIB_R71C3:BANKREF8", "CIB_R70C2:CIB_PLL2", "CIB_R70C3:CIB_PLL3"])),
    ((70, 88), "45K_", FuzzConfig(job="PLLROUTE2", family="ECP5", device="LFE5U-45F", ncl="pllroute.ncl",
                                 tiles=["MIB_R71C88:PLL0_LR", "MIB_R71C87:PLL1_LR", "CIB_R70C87:CIB_PLL3", "CIB_R70C88:CIB_PLL2"])),
    ((4, 89), "45K_", FuzzConfig(job="PLLROUTE3", family="ECP5", device="LFE5U-45F", ncl="pllroute.ncl",
                                  tiles=["MIB_R4C90:PLL0_UR", "MIB_R5C90:PLL1_UR", "CIB_R4C89:CIB_PLL0", "CIB_R5C89:CIB_PLL1"])),

    ((4, 1), "85K_", FuzzConfig(job="PLLROUTE0", family="ECP5", device="LFE5U-85F", ncl="pllroute_85k.ncl",
                                tiles=["MIB_R4C0:PLL0_UL", "MIB_R5C0:PLL1_UL", "CIB_R4C1:CIB_PLL0", "CIB_R5C1:CIB_PLL1"])),
    ((94, 2), "85K_", FuzzConfig(job="PLLROUTE1", family="ECP5", device="LFE5U-85F", ncl="pllroute_85k.ncl",
                                 tiles=["MIB_R95C2:PLL0_LL", "MIB_R95C3:BANKREF8"])),
    ((94, 124), "85K_", FuzzConfig(job="PLLROUTE2", family="ECP5", device="LFE5U-85F", ncl="pllroute_85k.ncl",
                                  tiles=["MIB_R95C124:PLL0_LR", "MIB_R95C123:BANKREF4"])),
    ((4, 125), "85K_", FuzzConfig(job="PLLROUTE3", family="ECP5", device="LFE5U-85F", ncl="pllroute_85k.ncl",
                                 tiles=["MIB_R4C126:PLL0_UR", "MIB_R5C126:PLL1_UR"])),

    ((49, 2), "25K_", FuzzConfig(job="PLLROUTE1", family="ECP5", device="LFE5U-25F", ncl="pllroute_25k.ncl",
                                 tiles=["MIB_R50C2:PLL0_LL", "MIB_R50C3:BANKREF8"])),
    ((49, 70), "25K_", FuzzConfig(job="PLLROUTE2", family="ECP5", device="LFE5U-25F", ncl="pllroute_25k.ncl",
                                  tiles=["MIB_R50C70:PLL0_LR", "MIB_R50C69:PLL1_LR"])),

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
