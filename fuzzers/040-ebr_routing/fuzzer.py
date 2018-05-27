from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

jobs = [
    ((25, 22), FuzzConfig(job="EBROUTE0", family="ECP5", device="LFE5U-25F", ncl="ebrroute.ncl",
                          tiles=["MIB_R25C22:MIB_EBR0", "MIB_R25C23:MIB_EBR1"])),
    ((25, 24), FuzzConfig(job="EBROUTE1", family="ECP5", device="LFE5U-25F", ncl="ebrroute.ncl",
                          tiles=["MIB_R25C24:MIB_EBR2", "MIB_R25C25:MIB_EBR3", "MIB_R25C26:MIB_EBR4"])),
    ((25, 26), FuzzConfig(job="EBROUTE2", family="ECP5", device="LFE5U-25F", ncl="ebrroute.ncl",
                          tiles=["MIB_R25C26:MIB_EBR4", "MIB_R25C27:MIB_EBR5", "MIB_R25C28:MIB_EBR6"])),
    ((25, 28), FuzzConfig(job="EBROUTE3", family="ECP5", device="LFE5U-25F", ncl="ebrroute.ncl",
                          tiles=["MIB_R25C28:MIB_EBR6", "MIB_R25C29:MIB_EBR7", "MIB_R25C30:MIB_EBR8"])),

]


def main():
    pytrellis.load_database("../../database")
    for job in jobs:
        loc, cfg = job
        cfg.setup()

        def nn_filter(net, netnames):
            return "EBR" in net

        interconnect.fuzz_interconnect(config=cfg, location=loc,
                                       netname_predicate=nn_filter,
                                       netname_filter_union=False,
                                       func_cib=True)


if __name__ == "__main__":
    main()
