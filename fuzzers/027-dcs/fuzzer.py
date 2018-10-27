from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

jobs = [
    FuzzConfig(job="DCS_45k", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
               tiles=["MIB_R10C39:EBR_CMUX_UL", "MIB_R10C40:CMUX_UL_0", "MIB_R10C41:CMUX_UR_0",
                      "MIB_R10C42:EBR_CMUX_UR", "MIB_R58C39:EBR_CMUX_LL", "MIB_R58C40:CMUX_LL_0",
                      "MIB_R58C41:CMUX_LR_0", "MIB_R58C42:EBR_CMUX_LR"]),
    FuzzConfig(job="DCS_25k", family="ECP5", device="LFE5U-25F", ncl="empty_25k.ncl",
               tiles=["MIB_R13C31:DSP_CMUX_UL", "MIB_R13C31:CMUX_UL_0",
                      "MIB_R13C32:CMUX_UR_0", "MIB_R13C32:DSP_CMUX_UR",
                      "MIB_R37C30:EBR_CMUX_LL_25K", "MIB_R37C31:CMUX_LL_0",
                      "MIB_R37C32:CMUX_LR_0", "MIB_R37C33:EBR_CMUX_LR_25K"]),
    FuzzConfig(job="DCS_85k", family="ECP5", device="LFE5U-85F", ncl="empty_85k.ncl",
               tiles=["MIB_R22C66:EBR_CMUX_UL", "MIB_R22C67:CMUX_UL_0",
                      "MIB_R22C68:CMUX_UR_0", "MIB_R22C69:EBR_CMUX_UR",
                      "MIB_R70C66:EBR_CMUX_LL", "MIB_R70C67:CMUX_LL_0",
                      "MIB_R70C68:CMUX_LR_0", "MIB_R70C69:EBR_CMUX_LR"])
]


def main():
    pytrellis.load_database("../../database")

    def per_job(job):
        cfg = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        if cfg.ncl == "empty_25k.ncl":
            cfg.ncl = "dcs_25k.ncl"
        elif cfg.ncl == "empty_85k.ncl":
            cfg.ncl = "dcs_85k.ncl"
        else:
            cfg.ncl = "dcs.ncl"
        for loc in ("DCS0", "DCS1"):
            def get_substs(dcsmode="POS"):
                if dcsmode == "NONE":
                    comment = "//"
                else:
                    comment = ""
                return dict(site=loc, comment=comment, dcsmode=dcsmode)

            nonrouting.fuzz_enum_setting(cfg, "{}.DCSMODE".format(loc),
                                         ["NONE", "POS", "NEG", "CLK0", "CLK1", "CLK0_LOW", "CLK0_HIGH", "CLK1_LOW",
                                          "CLK1_HIGH", "LOW", "HIGH"],
                                         lambda x: get_substs(dcsmode=x), empty_bitfile, False)

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
