from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

cfg = FuzzConfig(job="PIOROUTE", family="ECP5", device="LFE5U-25F", ncl="pioroute.ncl",
                 tiles=["MIB_R26C0:PICL0", "MIB_R27C0:PICL1", "MIB_R28C0:PICL2"])


def main():
    pytrellis.load_database("../../database")
    cfg.setup()

    def nn_filter(net, netnames):
        return not nets.is_cib(net)

    interconnect.fuzz_interconnect(config=cfg, location=(26, 0),
                                   netname_predicate=nn_filter,
                                   netname_filter_union=False,
                                   func_cib=True)
    interconnect.fuzz_interconnect(config=cfg, location=(27, 0),
                                   netname_predicate=nn_filter,
                                   netname_filter_union=False,
                                   func_cib=True)
    interconnect.fuzz_interconnect(config=cfg, location=(28, 0),
                                   netname_predicate=nn_filter,
                                   netname_filter_union=False,
                                   func_cib=True)


if __name__ == "__main__":
    main()
