from fuzzconfig import FuzzConfig
import interconnect
import pytrellis

jobs = [
    {
        "cfg": FuzzConfig(job="LMID_45K", family="ECP5", device="LFE5U-45F", ncl="emux_45k.ncl",
                          tiles=["MIB_R34C3:LMID_0"]),
        "mux_output": "R34C21_HPFE{:02d}00",
        "dcc_loc": "R34C1",
        "dcc_pos": "L",
        "size": 14,
        "prefix": "45K_",
        "cibclk": ["R34C1_JLLQPCLKCIB1", "R34C1_JLLQPCLKCIB0", "R34C1_JLLMPCLKCIB0"]
    },
    {
        "cfg": FuzzConfig(job="RMID_45K", family="ECP5", device="LFE5U-45F", ncl="emux_45k.ncl",
                          tiles=["MIB_R34C87:RMID_0"]),
        "mux_output": "R34C65_HPFW{:02d}00",
        "dcc_loc": "R34C89",
        "dcc_pos": "R",
        "size": 14,
        "prefix": "45K_",
        "cibclk": ["R34C89_JLRQPCLKCIB1", "R34C89_JLRQPCLKCIB0", "R34C89_JLRMPCLKCIB0"]
    },
    {
        "cfg": FuzzConfig(job="TMID_45K", family="ECP5", device="LFE5U-45F", ncl="emux_45k.ncl",
                          tiles=["MIB_R0C40:TMID_0", "MIB_R0C41:TMID_1"]),
        "mux_output": "R18C40_VPFS{:02d}00",
        "dcc_loc": "R1C40",
        "dcc_pos": "T",
        "size": 12,
        "prefix": "45K_",
        "cibclk": ["R1C40_JTRQPCLKCIB1", "R1C40_JTRQPCLKCIB0", "R1C40_JURMPCLKCIB1"]
    },
    {
        "cfg": FuzzConfig(job="BMID_45K", family="ECP5", device="LFE5U-45F", ncl="emux_45k.ncl",
                          tiles=["MIB_R71C40:BMID_0V", "MIB_R71C41:BMID_2V"]),
        "mux_output": "R52C40_VPFN{:02d}00",
        "dcc_loc": "R70C40",
        "dcc_pos": "B",
        "size": 16,
        "prefix": "45K_",
        "cibclk": ["R70C40_JBRQPCLKCIB1", "R70C40_JBRQPCLKCIB0", "R70C40_JLRMPCLKCIB1"]
    },
]


def get_sinks(job):
    # Get the sinks to fuzz for a given edgemux job
    sinks = []
    size = job["size"]
    sinks += [job["mux_output"].format(i) for i in range(size)]
    for dcc in range(size):
        loc = job["dcc_loc"]
        pos = job["dcc_pos"]
        sinks.append("{}_CLKI_{}DCC{}".format(loc, pos, dcc))
        sinks.append("{}_JCE_{}DCC{}".format(loc, pos, dcc))
        sinks.append("{}_{}DCC{}CLKI".format(loc, pos, dcc))
    sinks += job["cibclk"]
    return sinks


def main():
    pytrellis.load_database("../../database")
    for job in jobs:
        cfg = job["cfg"]
        cfg.setup()
        netnames = get_sinks(job)
        interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=netnames,
                                                     netname_filter_union=False,
                                                     full_mux_style=True,
                                                     fc_prefix=job["prefix"])


if __name__ == "__main__":
    main()
