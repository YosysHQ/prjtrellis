import sys

from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

cfg = FuzzConfig(job="OSCH", family="MachXO2", device="LCMXO2-1200HC", ncl="empty.ncl",
                                          tiles=["PT8:PIC_T_DUMMY_OSC",
                                                "PT4:CFG0", "PT5:CFG1",
                                                "PT6:CFG2", "PT7:CFG3",
                                                "CIB_R1C4:CIB_CFG0",
                                                "CIB_R1C5:CIB_CFG1"])


def get_substs(mode="OSCH", nom_freq="2.08"):
    if mode == "NONE":
        comment = "//"
    else:
        comment = ""

    if nom_freq == "2.08":
        using_non_default_freq = ""
        using_default_freq = "//"
    else:
        using_non_default_freq = "//"
        using_default_freq = ""

    return dict(comment=comment,
                nom_freq=nom_freq,
                using_non_default_freq=using_non_default_freq,
                using_default_freq=using_default_freq)

def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "osc.ncl"

    # Takes a long time, so permit opt-out.
    if "-s" not in sys.argv:
        nonrouting.fuzz_enum_setting(cfg, "OSCH.MODE", ["NONE", "OSCH"],
                                     lambda x: get_substs(mode=x), empty_bitfile)
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

    cfg.ncl = "osc_routing.ncl"
    interconnect.fuzz_interconnect_with_netnames(
        cfg,
        ["R1C4_JOSC_OSC"],
        bidir=True,
        netdir_override={"R1C4_JOSC_OSC" : "driver"},
        bias=1
    )

if __name__ == "__main__":
    main()
