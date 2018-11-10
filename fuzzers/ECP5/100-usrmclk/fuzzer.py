from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

cfg = FuzzConfig(job="USRMCLK", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                                          tiles=["MIB_R71C5:EFB1_PICB1", "MIB_R71C7:EFB3_PICB1"])


def get_substs(mode="USRMCLK"):
    if mode == "NONE":
        comment = "//"
    else:
        comment = ""
    return dict(comment=comment)
def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "cclk.ncl"

    nonrouting.fuzz_enum_setting(cfg, "CCLK.MODE", ["NONE", "USRMCLK"],
                                 lambda x: get_substs(mode=x), empty_bitfile)
    cfg.ncl = "cclk_routing.ncl"
    interconnect.fuzz_interconnect_with_netnames(
        cfg,
        ["R71C0_JPADDT_CCLK", "R71C0_JPADDO_CCLK", "R71C0_JPADDI_CCLK"],
        bidir=True
    )

if __name__ == "__main__":
    main()

