from fuzzconfig import FuzzConfig
import interconnect
import pytrellis

jobs = [
    {
        "cfg": FuzzConfig(job="BMID_45K", family="ECP5", device="LFE5UM5G-45F", ncl="emux_45k.ncl",
                          tiles=["MIB_R71C40:BMID_0H", "MIB_R71C41:BMID_2"]),
        "mux_output": "R52C40_VPFN{:02d}00",
        "dcc_loc": "R70C40",
        "dcc_pos": "B",
        "size": 16,
        "prefix": "45K_",
        "cibclk": ["R70C40_JBLQPCLKCIB0", "R70C40_JBLQPCLKCIB1", "R70C40_JLLMPCLKCIB1", "R70C40_JBRQPCLKCIB1", "R70C40_JBRQPCLKCIB0", "R70C40_JLRMPCLKCIB1"]
    },
    {
        "cfg": FuzzConfig(job="BMID_25K", family="ECP5", device="LFE5UM5G-25F", ncl="emux_25k.ncl",
                          tiles=["MIB_R50C31:BMID_0H", "MIB_R50C32:BMID_2"]),
        "mux_output": "R37C31_VPFN{:02d}00",
        "dcc_loc": "R49C31",
        "dcc_pos": "B",
        "size": 16,
        "prefix": "25K_",
        "cibclk": ["R49C31_JBLQPCLKCIB0", "R49C31_JBLQPCLKCIB1", "R49C31_JLLMPCLKCIB1", "R49C31_JLRMPCLKCIB1", "R49C31_JBRQPCLKCIB0", "R49C31_JBRQPCLKCIB1"]
    },

    {
        "cfg": FuzzConfig(job="BMID_85K", family="ECP5", device="LFE5UM5G-85F", ncl="emux_85k.ncl",
                          tiles=["MIB_R95C67:BMID_0H", "MIB_R95C68:BMID_2"]),
        "mux_output": "R70C67_VPFN{:02d}00",
        "dcc_loc": "R94C67",
        "dcc_pos": "B",
        "size": 16,
        "prefix": "85K_",
        "cibclk": ["R94C67_JBLQPCLKCIB0", "R94C67_JBLQPCLKCIB1", "R94C67_JLLMPCLKCIB1", "R94C67_JLLMPCLKCIB3", "R94C67_JLRMPCLKCIB1", "R94C67_JLRMPCLKCIB3", "R94C67_JBRQPCLKCIB0", "R94C67_JBRQPCLKCIB1"]
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
    pytrellis.load_database("../../../database")
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
