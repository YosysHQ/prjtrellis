from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

def dcu_tiles(r, c):
    return [f"MIB_R{r:02}C{c+i:02}:DCU{i}" for i in range(9)]

cfg = FuzzConfig(job="EXTREF", family="ECP5", device="LFE5UM5G-45F", ncl="empty.ncl",
                 tiles=dcu_tiles(71, 42))

rcfg_85k = FuzzConfig(job="EXTREF", family="ECP5", device="LFE5UM5G-85F", ncl="extref_routing_85k.ncl",
                 tiles=dcu_tiles(95, 46))

def get_substs(mode="EXTREFB", program=None):
    if mode == "NONE":
        comment = "//"
    else:
        comment = ""
    if program is not None:
        program = ":::" + ",".join(["{}={}".format(k, v) for k, v in program.items()])
    else:
        program = ":#ON"
    return dict(comment=comment, program=program)


def tobinstr(x, size):
    return "0b" + "".join(reversed(["1" if x else "0" for x in x]))


def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "extref.ncl"

    nonrouting.fuzz_enum_setting(cfg, "EXTREF.MODE", ["NONE", "EXTREFB"],
                                 lambda x: get_substs(mode=x, program={"REFCK_PWDNB": "0b0", "REFCK_RTERM": "0b0",
                                                                       "REFCK_DCBIAS_EN": "0b0"}), empty_bitfile, False)

    nonrouting.fuzz_word_setting(cfg, "EXTREF.REFCK_PWDNB", 1,
                                 lambda x: get_substs(program={"REFCK_PWDNB": tobinstr(x, 1)}), empty_bitfile)
    nonrouting.fuzz_word_setting(cfg, "EXTREF.REFCK_RTERM", 1,
                                 lambda x: get_substs(program={"REFCK_RTERM": tobinstr(x, 1)}), empty_bitfile)
    nonrouting.fuzz_word_setting(cfg, "EXTREF.REFCK_DCBIAS_EN", 1,
                                 lambda x: get_substs(program={"REFCK_DCBIAS_EN": tobinstr(x, 1)}), empty_bitfile)

    cfg.ncl = "extref_routing.ncl"
    interconnect.fuzz_interconnect_with_netnames(
        cfg,
        ["R71C42_REFCLKP_EXTREF",
         "R71C42_INPUT_REFP_APIO",
         "R71C42_OUTPUT_REFP_APIO",
         "R71C42_CLK_REFP_APIO",
         "R71C42_REFCLKN_EXTREF",
         "R71C42_INPUT_REFN_APIO",
         "R71C42_OUTPUT_REFN_APIO",
         "R71C42_CLK_REFN_APIO",
         "R71C42_JREFCLKO_EXTREF",
         "R71C42_EXTREFCLK",
         "R71C42_JTXREFCLKCIB",
         "R71C42_JCH1RXREFCLKCIB",
         "R71C42_JCH0RXREFCLKCIB",
         "R71C42_CH0_RX_REFCLK",
         "R71C42_CH1_RX_REFCLK",
         "R71C42_D_REFCLKI",
         "R71C42_RXREFCLK0",
         "R71C42_RXREFCLK1",
         "R71C42_JTXREFCLK"],
        bidir=True
    )

    rcfg_85k.setup()
    interconnect.fuzz_interconnect_with_netnames(
        rcfg_85k,
        ["R95C46_JREFCLKO_EXTREF"],
        bidir=True
    )


if __name__ == "__main__":
    main()
