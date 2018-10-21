from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

jobs = [
    ((71, 42), FuzzConfig(job="DCUROUTE0", family="ECP5", device="LFE5UM5G-45F", ncl="dcuroute.ncl",
                          tiles=["MIB_R71C42:DCU0", "MIB_R71C43:DCU1", "MIB_R71C44:DCU2", "MIB_R71C45:DCU3",
                                 "MIB_R71C46:DCU4", "MIB_R71C47:DCU5", "MIB_R71C48:DCU6", "MIB_R71C49:DCU7",
                                 "MIB_R71C50:DCU8"]))

]


def main():
    pytrellis.load_database("../../database")
    for job in jobs:
        loc, cfg = job
        cfg.setup()

        def nn_filter(net, netnames):
            return "DCU" in net or "PCS" in net

        interconnect.fuzz_interconnect(config=cfg, location=loc,
                                       netname_predicate=nn_filter,
                                       netname_filter_union=False,
                                       func_cib=True)


if __name__ == "__main__":
    main()
