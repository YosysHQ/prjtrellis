from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

cfg = FuzzConfig(job="JTAG", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                                          tiles=["MIB_R71C4:EFB0_PICB0", "MIB_R71C5:EFB1_PICB1"])


def get_substs(mode="JTAGG", er1="DISABLED", er2="DISABLED"):
    if mode == "NONE":
        comment = "//"
    else:
        comment = ""
    return dict(comment=comment, er1=er1, er2=er2)

def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "jtag.ncl"

    nonrouting.fuzz_enum_setting(cfg, "JTAG.MODE", ["NONE", "JTAGG"],
                                 lambda x: get_substs(mode=x), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "JTAG.ER1", ["DISABLED", "ENABLED"],
                                 lambda x: get_substs(er1=x), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "JTAG.ER2", ["DISABLED", "ENABLED"],
                                 lambda x: get_substs(er2=x), empty_bitfile, False)
    cfg.ncl = "jtag_routing.ncl"
    interconnect.fuzz_interconnect_with_netnames(
        cfg,
        ["R70C4_JJTDO1_JTAG",
         "R70C4_JJTDO2_JTAG",
         "R70C4_JTCK_JTAG",
         "R70C4_JTMS_JTAG",
         "R70C4_JTDI_JTAG",
         "R70C4_JJTDI_JTAG",
         "R70C4_JJTCK_JTAG",
         "R70C4_JJRTI1_JTAG",
         "R70C4_JJRTI2_JTAG",
         "R70C4_JJSHIFT_JTAG",
         "R70C4_JJUPDATE_JTAG",
         "R70C4_JJRSTN_JTAG",
         "R70C4_JJCE1_JTAG",
         "R70C4_JJCE2_JTAG",
         "R70C4_JTDO_JTAG"],
        bidir=True
    )


if __name__ == "__main__":
    main()

