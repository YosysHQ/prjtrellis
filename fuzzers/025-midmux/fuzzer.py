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
        "cibclk": ["R34C1_JLLQPCLKCIB1", "R34C1_JLLQPCLKCIB0", "R34C1_JLLMPCLKCIB0", "R34C1_JULQPCLKCIB0", "R34C1_JULQPCLKCIB1", "R34C1_JULMPCLKCIB0"]
    },
    {
        "cfg": FuzzConfig(job="RMID_45K", family="ECP5", device="LFE5U-45F", ncl="emux_45k.ncl",
                          tiles=["MIB_R34C87:RMID_0"]),
        "mux_output": "R34C65_HPFW{:02d}00",
        "dcc_loc": "R34C89",
        "dcc_pos": "R",
        "size": 14,
        "prefix": "45K_",
        "cibclk": ["R34C89_JLRQPCLKCIB1", "R34C89_JLRQPCLKCIB0", "R34C89_JLRMPCLKCIB0", "R34C89_JURQPCLKCIB1", "R34C89_JURQPCLKCIB0", "R34C89_JURMPCLKCIB0"]
    },
    {
        "cfg": FuzzConfig(job="TMID_45K", family="ECP5", device="LFE5U-45F", ncl="emux_45k.ncl",
                          tiles=["MIB_R0C40:TMID_0", "MIB_R0C41:TMID_1"]),
        "mux_output": "R18C40_VPFS{:02d}00",
        "dcc_loc": "R1C40",
        "dcc_pos": "T",
        "size": 12,
        "prefix": "45K_",
        "cibclk": ["R1C40_JTRQPCLKCIB1", "R1C40_JTRQPCLKCIB0", "R1C40_JURMPCLKCIB1", "R1C40_JULMPCLKCIB1", "R1C40_JTLQPCLKCIB0", "R1C40_JTLQPCLKCIB1"]
    },
    {
        "cfg": FuzzConfig(job="BMID_45K", family="ECP5", device="LFE5U-45F", ncl="emux_45k.ncl",
                          tiles=["MIB_R71C40:BMID_0V", "MIB_R71C41:BMID_2V"]),
        "mux_output": "R52C40_VPFN{:02d}00",
        "dcc_loc": "R70C40",
        "dcc_pos": "B",
        "size": 16,
        "prefix": "45K_",
        "cibclk": ["R70C40_JBLQPCLKCIB0", "R70C40_JBLQPCLKCIB1", "R70C40_JLLMPCLKCIB1", "R70C40_JBRQPCLKCIB1", "R70C40_JBRQPCLKCIB0", "R70C40_JLRMPCLKCIB1"]
    },

    {
        "cfg": FuzzConfig(job="LMID_25K", family="ECP5", device="LFE5U-25F", ncl="emux_25k.ncl",
                          tiles=["MIB_R25C3:LMID_0"]),
        "mux_output": "R25C16_HPFE{:02d}00",
        "dcc_loc": "R25C1",
        "dcc_pos": "L",
        "size": 14,
        "prefix": "25K_",
        "cibclk": ["R25C1_JLLQPCLKCIB1", "R25C1_JLLQPCLKCIB0", "R25C1_JLLMPCLKCIB0" "R25C1_JULQPCLKCIB1", "R25C1_JULQPCLKCIB0", "R25C1_JULMPCLKCIB0"]
    },
    {
        "cfg": FuzzConfig(job="RMID_25K", family="ECP5", device="LFE5U-25F", ncl="emux_25k.ncl",
                          tiles=["MIB_R25C69:RMID_0"]),
        "mux_output": "R25C51_HPFW{:02d}00",
        "dcc_loc": "R25C71",
        "dcc_pos": "R",
        "size": 14,
        "prefix": "25K_",
        "cibclk": ["R25C71_JLRQPCLKCIB1", "R25C71_JLRQPCLKCIB1", "R25C71_JLRMPCLKCIB0", "R25C71_JURQPCLKCIB1", "R25C71_JURQPCLKCIB0", "R25C71_JURMPCLKCIB0"]
    },
    {
        "cfg": FuzzConfig(job="TMID_25K", family="ECP5", device="LFE5U-25F", ncl="emux_25k.ncl",
                          tiles=["MIB_R0C31:TMID_0", "MIB_R0C32:TMID_1"]),
        "mux_output": "R13C31_VPFS{:02d}00",
        "dcc_loc": "R1C31",
        "dcc_pos": "T",
        "size": 12,
        "prefix": "25K_",
        "cibclk": ["R1C31_JULMPCLKCIB1", "R1C31_JTLQPCLKCIB0", "R1C31_JTLQPCLKCIB1", "R1C31_JURMPCLKCIB1", "R1C31_JTRQPCLKCIB0", "R1C31_JTRQPCLKCIB1"]
    },
    {
        "cfg": FuzzConfig(job="BMID_25K", family="ECP5", device="LFE5U-25F", ncl="emux_25k.ncl",
                          tiles=["MIB_R50C31:BMID_0V", "MIB_R50C32:BMID_2V"]),
        "mux_output": "R37C31_VPFN{:02d}00",
        "dcc_loc": "R49C31",
        "dcc_pos": "B",
        "size": 16,
        "prefix": "25K_",
        "cibclk": ["R49C31_JBLQPCLKCIB0", "R49C31_JBLQPCLKCIB1", "R49C31_JLLMPCLKCIB1", "R49C31_JLRMPCLKCIB1", "R49C31_JBRQPCLKCIB0", "R49C31_JBRQPCLKCIB1"]
    },

    {
        "cfg": FuzzConfig(job="LMID_85K", family="ECP5", device="LFE5U-85F", ncl="emux_85k.ncl",
                          tiles=["MIB_R46C3:LMID_0"]),
        "mux_output": "R46C34_HPFE{:02d}00",
        "dcc_loc": "R46C1",
        "dcc_pos": "L",
        "size": 14,
        "prefix": "85K_",
        "cibclk": ["R46C1_JLLQPCLKCIB1", "R46C1_JLLQPCLKCIB0", "R46C1_JLLMPCLKCIB2", "R46C1_JLLMPCLKCIB0", "R46C1_JULQPCLKCIB1", "R46C1_JULQPCLKCIB0", "R46C1_JULMPCLKCIB2", "R46C1_JULMPCLKCIB0"]
    },
    {
        "cfg": FuzzConfig(job="RMID_85K", family="ECP5", device="LFE5U-85F", ncl="emux_85k.ncl",
                          tiles=["MIB_R46C123:RMID_0"]),
        "mux_output": "R46C96_HPFW{:02d}00",
        "dcc_loc": "R46C125",
        "dcc_pos": "R",
        "size": 14,
        "prefix": "85K_",
        "cibclk": ["R46C125_JLRQPCLKCIB1", "R46C125_JLRQPCLKCIB0", "R46C125_JLRMPCLKCIB2", "R46C125_JLRMPCLKCIB0", "R46C125_JURQPCLKCIB1", "R46C125_JURQPCLKCIB0", "R46C125_JURMPCLKCIB2", "R46C125_JURMPCLKCIB0"]
    },
    {
        "cfg": FuzzConfig(job="TMID_85K", family="ECP5", device="LFE5U-85F", ncl="emux_85k.ncl",
                          tiles=["MIB_R0C67:TMID_0", "MIB_R0C68:TMID_1"]),
        "mux_output": "R24C67_VPFS{:02d}00",
        "dcc_loc": "R1C67",
        "dcc_pos": "T",
        "size": 12,
        "prefix": "85K_",
        "cibclk": ["R1C67_JULMPCLKCIB1", "R1C67_JULMPCLKCIB3", "R1C67_JTLQPCLKCIB0", "R1C67_JTLQPCLKCIB1", "R1C67_JTRQPCLKCIB1", "R1C67_JTRQPCLKCIB0", "R1C67_JURMPCLKCIB3", "R1C67_JURMPCLKCIB1"]
    },
    {
        "cfg": FuzzConfig(job="BMID_85K", family="ECP5", device="LFE5U-85F", ncl="emux_85k.ncl",
                          tiles=["MIB_R95C67:BMID_0V", "MIB_R95C68:BMID_2V"]),
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
