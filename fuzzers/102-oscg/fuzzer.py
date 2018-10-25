from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

cfg = FuzzConfig(job="OSC", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                                          tiles=["MIB_R71C4:EFB0_PICB0", "MIB_R71C5:EFB1_PICB1", "CIB_R71C26:OSC"])


def get_substs(mode="OSC", div="0"):
    if mode == "NONE":
        comment = "//"
    else:
        comment = ""
    return dict(comment=comment, div=div)

def main():
    pytrellis.load_database("../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "osc.ncl"

    nonrouting.fuzz_enum_setting(cfg, "OSC.MODE", ["NONE", "OSCG"],
                                 lambda x: get_substs(mode=x), empty_bitfile)
    nonrouting.fuzz_enum_setting(cfg, "OSC.DIV", ["{}".format(i) for i in range(2, 128)],
                                 lambda x: get_substs(div=x), empty_bitfile)
    cfg.ncl = "osc_routing.ncl"
    interconnect.fuzz_interconnect_with_netnames(
        cfg,
        ["R70C4_JOSC_OSC"],
        bidir=True
    )

if __name__ == "__main__":
    main()

