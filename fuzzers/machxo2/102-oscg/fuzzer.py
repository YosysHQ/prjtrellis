from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect
import argparse

cfg = FuzzConfig(job="OSCH", family="MachXO2", device="LCMXO2-1200HC", ncl="empty.ncl",
                                          tiles=["PT8:PIC_T_DUMMY_OSC",
                                                "PT4:CFG0", "PT5:CFG1",
                                                "PT6:CFG2", "PT7:CFG3",
                                                "CIB_R1C4:CIB_CFG0",
                                                "CIB_R1C5:CIB_CFG1"])

cfg_r = FuzzConfig(job="OSCH_ROUTE", family="MachXO2", device="LCMXO2-1200HC", ncl="osc_routing.ncl",
                                          tiles=["CIB_R1C4:CIB_CFG0"])


def get_substs(mode="OSCH", nom_freq="2.08", stdby="0"):
    if mode == "NONE":
        comment = "//"
    else:
        comment = ""

    if stdby == "1":
        stdby = ""
        stdby_0 = "//"
    else:
        stdby = "//"
        stdby_0 = ""

    if nom_freq == "2.08":
        using_non_default_freq = ""
        using_default_freq = "//"
    else:
        using_non_default_freq = "//"
        using_default_freq = ""

    return dict(comment=comment,
                nom_freq=nom_freq,
                stdby=stdby,
                stdby_0=stdby_0,
                using_non_default_freq=using_non_default_freq,
                using_default_freq=using_default_freq)

def main(args):
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "osc.ncl"

    if args.e:
        nonrouting.fuzz_enum_setting(cfg, "OSCH.STDBY", ["0", "1"],
                                     lambda x: get_substs(stdby=x), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "OSCH.MODE", ["NONE", "OSCH"],
                                     lambda x: get_substs(mode=x), empty_bitfile)

    if args.f:
        nonrouting.fuzz_enum_setting(cfg, "OSCH.NOM_FREQ",
            ["{}".format(i) for i in [
                2.08, 2.15, 2.22, 2.29, 2.38, 2.46, 2.56, 2.66, 2.77, 2.89,
                3.02, 3.17, 3.33, 3.50, 3.69, 3.91, 4.16, 4.29, 4.43, 4.59,
                4.75, 4.93, 5.12, 5.32, 5.54, 5.78, 6.05, 6.33, 6.65, 7.00,
                7.39, 7.82, 8.31, 8.58, 8.87, 9.17, 9.50, 9.85, 10.23, 10.64,
                11.08, 11.57, 12.09, 12.67, 13.30, 14.00, 14.78, 15.65, 15.65, 16.63,
                17.73, 19.00, 20.46, 22.17, 24.18, 26.60, 29.56, 33.25, 38.00, 44.33,
                53.20, 66.50, 88.67, 133.00
            ]], lambda x: get_substs(nom_freq=x), empty_bitfile)

    if args.r:
        cfg_r.setup()
        interconnect.fuzz_interconnect_with_netnames(
            cfg_r,
            ["R1C4_JOSC_OSC",
            "R1C4_JSTDBY_OSC"],
            bidir=True,
            netdir_override={"R1C4_JOSC_OSC" : "driver",
                             "R1C4_JSTDBY_OSC" : "sink"})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OSCH Fuzzer.")
    parser.add_argument("-e", action="store_true", help="Fuzz other enums.")
    parser.add_argument("-f", action="store_true", help="Fuzz frequency enum.")
    parser.add_argument("-r", action="store_true", help="Fuzz routing.")
    args = parser.parse_args()
    main(args)
