from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import interconnect

cfg = FuzzConfig(job="SED", family="MachXO2", device="LCMXO2-1200HC", ncl="empty.ncl",
                                          tiles=["PT7:CFG3"])

cfg2 = FuzzConfig(job="SED", family="MachXO2", device="LCMXO2-1200HC", ncl="empty.ncl",
                                          tiles=["PT6:CFG2", "PT7:CFG3"])

def get_substs(exclk_used="NO", clk_freq="2.08", checkalways="DISABLED"):
    if clk_freq == "NONE":
        comment = "//"
    else:
        comment = ""
    if exclk_used == "YES" and clk_freq != "NONE":
        scomment = ""
    else:
        scomment = "//"
    return dict(comment=comment, scomment=scomment, clk_freq=clk_freq, checkalways=checkalways)

def get_substs_mode(mode):
    if mode == "NONE":
        comment = "//"
    else:
        comment = ""
    return dict(comment=comment, mode=mode)

def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "sed.ncl"
    freq = ["2.08", "4.16",  "8.31", "16.63",
            "2.15", "4.29",  "8.58", "17.73",
            "2.22", "4.43",  "8.87", "19.00",
            "2.29", "4.59",  "9.17", "20.46",
            "2.38", "4.75",  "9.50", "22.17",
            "2.46", "4.93",  "9.85", "24.18",
            "2.56", "5.12", "10.23", "26.60",
            "2.66", "5.32", "10.64", "29.56",
            "2.77", "5.54", "11.08", "33.25",
            "2.89", "5.78", "11.57",
            "3.02", "6.05", "12.09",
            "3.17", "6.33", "12.67",
            "3.33", "6.65", "13.30",
            "3.50", "7.00", "14.00",
            "3.69", "7.39", "14.78",
            "3.91", "7.82", "15.65"]
    nonrouting.fuzz_enum_setting(cfg, "SED.CLK_FREQ", freq,
                                 lambda x: get_substs(clk_freq=x), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SED.CHECKALWAYS", ["DISABLED", "ENABLED"],
                                 lambda x: get_substs(checkalways=x), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SED.SEDEXCLK_USED", ["YES", "NO"],
                                 lambda x: get_substs(exclk_used=x), empty_bitfile, False)
    cfg.ncl = "sed_routing.ncl"

    override_dict = { "R1C4_SEDSTDBY_SED" : "sink",
                "R1C4_JSEDENABLE_SED" : "sink",
                "R1C4_JSEDSTART_SED" : "sink",
                "R1C4_JSEDFRCERR_SED" : "sink",
                "R1C4_JSEDEXCLK_SED" : "sink",
                "R1C4_JSEDERR_SED" : "driver",
                "R1C4_JSEDDONE_SED" : "driver",
                "R1C4_JSEDINPROG_SED" : "driver",
                "R1C4_JAUTODONE_SED" : "driver"}

    nets = [net for net in override_dict]

    interconnect.fuzz_interconnect_with_netnames(
        cfg,
        nets,
        bidir=True,
        netdir_override=override_dict
    )
    cfg2.setup()
    cfg2.ncl = "sed_mode.ncl"
    nonrouting.fuzz_enum_setting(cfg2, "SED.MODE", ["SEDFA", "SEDFB", "NONE"],
                                 lambda x: get_substs_mode(mode=x), empty_bitfile, False)

if __name__ == "__main__":
    main()

