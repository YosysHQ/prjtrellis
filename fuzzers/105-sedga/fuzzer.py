from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

cfg = FuzzConfig(job="JTAG", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                                          tiles=["MIB_R71C4:EFB0_PICB0", "MIB_R71C5:EFB1_PICB1", "MIB_R71C6:EFB2_PICB0"])


def get_substs(exclk_used="YES", clk_freq="2.4", checkalways="DISABLED"):
    if clk_freq == "NONE":
        comment = "//"
    else:
        comment = ""
    if exclk_used == "YES" and clk_freq != "NONE":
        scomment = ""
    else:
        scomment = "//"
    return dict(comment=comment, scomment=scomment, clk_freq=clk_freq, checkalways=checkalways)


def main():
    pytrellis.load_database("../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "sed.ncl"

    nonrouting.fuzz_enum_setting(cfg, "SED.CLK_FREQ", ["NONE", "2.4", "4.8", "9.7", "19.4", "38.8", "62.0"],
                                 lambda x: get_substs(clk_freq=x), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SED.CHECKALWAYS", ["DISABLED", "ENABLED"],
                                 lambda x: get_substs(checkalways=x), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SED.SEDEXCLK_USED", ["YES", "NO"],
                                 lambda x: get_substs(exclk_used=x), empty_bitfile, False)
    cfg.ncl = "sed_routing.ncl"
    interconnect.fuzz_interconnect_with_netnames(
        cfg,
        ["R70C4_SEDSTDBY_SED",
         "R70C4_JSEDENABLE_SED",
         "R70C4_JSEDSTART_SED",
         "R70C4_JSEDFRCERR_SED",
         "R70C4_JSEDEXCLK_SED",
         "R70C4_JSEDERR_SED",
         "R70C4_JSEDDONE_SED",
         "R70C4_JSEDINPROG_SED",
         "R70C4_JAUTODONE_SED"
         ],
        bidir=True
    )


if __name__ == "__main__":
    main()

