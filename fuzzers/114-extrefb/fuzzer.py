from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

cfg = FuzzConfig(job="EXTREF", family="ECP5", device="LFE5UM5G-45F", ncl="empty.ncl",
                 tiles=["MIB_R71C42:DCU0", "MIB_R71C43:DCU1", "MIB_R71C44:DCU2", "MIB_R71C45:DCU3",
                        "MIB_R71C46:DCU4", "MIB_R71C47:DCU5", "MIB_R71C48:DCU6", "MIB_R71C49:DCU7",
                        "MIB_R71C50:DCU8"])


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
    pytrellis.load_database("../../database")
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


if __name__ == "__main__":
    main()
