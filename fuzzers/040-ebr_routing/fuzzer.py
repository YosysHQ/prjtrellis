from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

cfg = FuzzConfig(job="EBROUTE", family="ECP5", device="LFE5U-25F", ncl="ebrroute.ncl",
                 tiles=["MIB_R25C22:MIB_EBR0", "MIB_R25C23:MIB_EBR1"])


def main():
    pytrellis.load_database("../../database")
    cfg.setup()

    def nn_filter(net, netnames):
        return "EBR" in net

    interconnect.fuzz_interconnect(config=cfg, location=(25, 22),
                                   netname_predicate=nn_filter,
                                   netname_filter_union=False,
                                   func_cib=True)

if __name__ == "__main__":
    main()
