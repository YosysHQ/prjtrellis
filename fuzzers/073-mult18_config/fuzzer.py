from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops

dsp_tiles = [
    "MIB_R13C4:MIB_DSP0", "MIB_R13C4:MIB2_DSP0",
    "MIB_R13C5:MIB_DSP1", "MIB_R13C5:MIB2_DSP1",
    "MIB_R13C6:MIB_DSP2", "MIB_R13C6:MIB2_DSP2",
    "MIB_R13C7:MIB_DSP3", "MIB_R13C7:MIB2_DSP3",
    "MIB_R13C8:MIB_DSP4", "MIB_R13C8:MIB2_DSP4",
    "MIB_R13C9:MIB_DSP5", "MIB_R13C9:MIB2_DSP5",
    "MIB_R13C10:MIB_DSP6", "MIB_R13C10:MIB2_DSP6",
    "MIB_R13C11:MIB_DSP7", "MIB_R13C11:MIB2_DSP7",
    "MIB_R13C12:MIB_DSP8", "MIB_R13C12:MIB2_DSP8",
]

jobs = [
    ("MULT18_R13C4", "MULT18_0", FuzzConfig(job="MULT18_0", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                            tiles=dsp_tiles)),
]


def main():
    pytrellis.load_database("../../database")

    def per_job(job):
        def get_substs(settings, mode="MULT18X18D"):
            if mode == "NONE":
                comment = "//"
            else:
                comment = ""
            return dict(loc=loc, mode=mode, settings=",".join(["{}={}".format(k, v) for k, v in settings.items()]),
                        comment=comment)

        loc, mult, cfg = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "dspconfig.ncl"

        nonrouting.fuzz_enum_setting(cfg, "{}.MODE".format(mult), ["NONE", "MULT18X18D"],
                                     lambda x: get_substs(settings={}, mode=x), empty_bitfile, False)

        regs = ["INPUTA", "INPUTB", "INPUTC", "PIPELINE", "OUTPUT"]
        clks = ["NONE", "CLK0", "CLK1", "CLK2", "CLK3"]
        cens = ["CE0", "CE1", "CE2", "CE3"]
        rsts = ["RST0", "RST1", "RST2", "RST3"]
        for reg in regs:
            nonrouting.fuzz_enum_setting(cfg, "{}.REG_{}_CLK".format(mult, reg), clks,
                                         lambda x: get_substs(settings={"REG_{}_CLK".format(reg): x}), empty_bitfile,
                                         False)
            nonrouting.fuzz_enum_setting(cfg, "{}.REG_{}_CE".format(mult, reg), cens,
                                         lambda x: get_substs(settings={"REG_{}_CE".format(reg): x}), empty_bitfile,
                                         False)
            nonrouting.fuzz_enum_setting(cfg, "{}.REG_{}_RST".format(mult, reg), rsts,
                                         lambda x: get_substs(settings={"REG_{}_RST".format(reg): x}), empty_bitfile,
                                         False)
        for clk in ["CLK0", "CLK1", "CLK2", "CLK3"]:
            nonrouting.fuzz_enum_setting(cfg, "{}.{}_DIV".format(mult, clk), ["ENABLED", "DISABLED"],
                                         lambda x: get_substs(settings={"{}_DIV".format(clk): x}), empty_bitfile, False)

        nonrouting.fuzz_enum_setting(cfg, "{}.CAS_MATCH_REG".format(mult), ["FALSE", "TRUE"],
                                     lambda x: get_substs(settings={"CAS_MATCH_REG": x}), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "{}.MULT_BYPASS".format(mult), ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"MULT_BYPASS": x}), empty_bitfile, False)

        nonrouting.fuzz_enum_setting(cfg, "{}.GSR".format(mult), ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"GSR": x}), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "{}.RESETMODE".format(mult), ["SYNC", "ASYNC"],
                                     lambda x: get_substs(settings={"RESETMODE": x}), empty_bitfile, False)

        nonrouting.fuzz_enum_setting(cfg, "{}.SOURCEB_MODE".format(mult),
                                     ["B_SHIFT", "C_SHIFT", "B_C_DYNAMIC", "HIGHSPEED"],
                                     lambda x: get_substs(settings={"SOURCEB_MODE": x}), empty_bitfile, False)

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
