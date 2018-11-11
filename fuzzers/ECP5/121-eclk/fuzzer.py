from fuzzconfig import FuzzConfig
import interconnect
import pytrellis

jobs = [
    {
        "cfg": FuzzConfig(job="LECLK_45K", family="ECP5", device="LFE5U-45F", ncl="emux_45k.ncl",
                          tiles=["CIB_R34C2:ECLK_L"]),
        "eclk_loc": ["R34C0", "R35C0"],
        "prefix": "45K_",
        "bank_eclk": ["R18C0_BANK7ECLK0", "R18C0_BANK7ECLK1", "R53C0_BANK6ECLK0", "R53C0_BANK6ECLK1"],
        "eclk_i": ["R34C0_ECLKI0", "R35C0_ECLKI0", "R34C0_JECLKI1", "R35C0_JECLKI1"],
        "cibclk": ["R34C0_JULQECLKCIB0", "R34C0_JULQECLKCIB1", "R34C0_JLLQECLKCIB0", "R34C0_JLLQECLKCIB1"],
    },

    {
        "cfg": FuzzConfig(job="RECLK_45K", family="ECP5", device="LFE5U-45F", ncl="emux_45k.ncl",
                          tiles=["CIB_R34C88:ECLK_R"]),
        "eclk_loc": ["R34C90", "R35C90"],
        "prefix": "45K_",
        "bank_eclk": ["R18C90_BANK2ECLK0", "R18C90_BANK2ECLK1", "R53C90_BANK3ECLK0", "R53C90_BANK3ECLK1"],
        "eclk_i": ["R34C90_JECLKI0", "R35C90_JECLKI0", "R34C90_ECLKI1", "R35C90_ECLKI1"],
        "cibclk": ["R34C90_JURQECLKCIB0", "R34C90_JURQECLKCIB1", "R34C90_JLRQECLKCIB0", "R34C90_JLRQECLKCIB1"],
    },
]


def get_sinks(job):
    # Get the sinks to fuzz for a given edgemux job
    sinks = []
    sinks += job["eclk_i"]
    for loc in job["eclk_loc"]:
        for i in range(2):
            sinks.append("{}_ECLKI_ECLKSYNC{}".format(loc, i))
            sinks.append("{}_JSTOP_ECLKSYNC{}".format(loc, i))
            sinks.append("{}_JECLKO_ECLKSYNC{}".format(loc, i))
            sinks.append("{}_SYNCECLK{}".format(loc, i))
            sinks.append("{}_JNEIGHBORECLK{}".format(loc, i))
            sinks.append("{}_JBRGECLK{}".format(loc, i))
            sinks.append("{}_JECLK{}".format(loc, i))
    sinks += job["bank_eclk"]
    sinks += job["cibclk"]
    return sinks


def main():
    pytrellis.load_database("../../../database")
    for job in jobs:
        cfg = job["cfg"]
        cfg.setup()
        netnames = get_sinks(job)
        interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=netnames,
                                                     netname_filter_union=False,
                                                     full_mux_style=True,
                                                     nonlocal_prefix=job["prefix"])


if __name__ == "__main__":
    main()
