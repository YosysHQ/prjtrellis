from fuzzconfig import FuzzConfig
import interconnect
import pytrellis

jobs = [
    {
        "cfg": FuzzConfig(job="LECLK_45K", family="ECP5", device="LFE5U-45F", ncl="emux_45k.ncl",
                          tiles=["CIB_R34C2:ECLK_L"]),
        "prim": 1,
        "loc": "R34C0",
        "globals": ["R34C40_JLECLK1", "R34C40_JBRGECLK1"],
    },

    {
        "cfg": FuzzConfig(job="RECLK_45K", family="ECP5", device="LFE5U-45F", ncl="emux_45k.ncl",
                          tiles=["CIB_R34C88:ECLK_R"]),
        "prim": 0,
        "loc": "R34C90",
        "globals": ["R34C40_JRECLK0", "R34C40_JBRGECLK0"],
    },
]


def get_sinks(job):
    # Get the sinks to fuzz for a given edgemux job
    loc = job["loc"]
    prim = job["prim"]
    sinks = []
    sinks.append("{}_JCLK0_ECLKBRIDGECS{}".format(loc, prim))
    sinks.append("{}_JCLK1_ECLKBRIDGECS{}".format(loc, prim))
    sinks.append("{}_JSEL_ECLKBRIDGECS{}".format(loc, prim))
    sinks.append("{}_ECLKI_BRGECLKSYNC{}".format(loc, prim))
    sinks.append("{}_JSTOP_BRGECLKSYNC{}".format(loc, prim))
    sinks += job["globals"]
    return sinks


def main():
    pytrellis.load_database("../../../database")
    for job in jobs:
        cfg = job["cfg"]
        cfg.setup()
        netnames = get_sinks(job)
        interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=netnames,
                                                     netname_filter_union=False,
                                                     full_mux_style=True)


if __name__ == "__main__":
    main()
