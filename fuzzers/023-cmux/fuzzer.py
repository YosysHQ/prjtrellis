from fuzzconfig import FuzzConfig
import interconnect
import pytrellis

jobs = [
    {
        "cfg": FuzzConfig(job="CMUX_45k", family="ECP5", device="LFE5U-45F", ncl="cmux_45k.ncl",
                          tiles=["MIB_R10C39:EBR_CMUX_UL", "MIB_R10C40:CMUX_UL_0", "MIB_R10C41:CMUX_UR_0",
                                 "MIB_R10C42:EBR_CMUX_UR", "MIB_R58C39:EBR_CMUX_LL", "MIB_R58C40:CMUX_LL_0",
                                 "MIB_R58C41:CMUX_LR_0", "MIB_R58C42:EBR_CMUX_LR"]),
        "cmux_outputs": ["R22C40_ULPCLK{}", "R22C40_URPCLK{}", "R46C40_LLPCLK{}", "R46C40_LRPCLK{}"],
        "dcc_loc": "R34C40",
        "dcs_loc": "R34C40",
        "prefix": "45K_"
    }
]


def get_sinks(job):
    # Get the sinks to fuzz for a given cmux job
    sinks = []
    for out in job["cmux_outputs"]:
        sinks += [out.format(i) for i in range(16)]
    for dcc in ["TL", "TR", "BL", "BR"]:
        loc = job["dcc_loc"]
        sinks.append("{}_JCLKI_DCC{}".format(loc, dcc))
        sinks.append("{}_JCE_DCC{}".format(loc, dcc))
        quad = dcc.replace("T", "U").replace("B", "L")
        sinks.append("{}_{}CPCLKCIB0".format(loc, quad))
    for dcs in range(2):
        loc = job["dcs_loc"]
        sinks.append("{}_CLK0_DCS{}".format(loc, dcs))
        sinks.append("{}_CLK1_DCS{}".format(loc, dcs))
        sinks.append("{}_DCS{}CLK0".format(loc, dcs))
        sinks.append("{}_DCS{}CLK1".format(loc, dcs))
        sinks.append("{}_DCS{}".format(loc, dcs))
        sinks.append("{}_JSEL0_DCS{}".format(loc, dcs))
        sinks.append("{}_JSEL1_DCS{}".format(loc, dcs))
        sinks.append("{}_JMODESEL_DCS{}".format(loc, dcs))
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
