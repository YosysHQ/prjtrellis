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
    ("MULT18_R13C4", "DSP_LEFT", FuzzConfig(job="DSP_LEFT", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                            tiles=dsp_tiles)),
    ("MULT18_R13C8", "DSP_RIGHT", FuzzConfig(job="DSP_RIGHT", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                             tiles=dsp_tiles)),
    ("MULT18_R13C4", "MULT18_0", FuzzConfig(job="MULT18_0", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                            tiles=dsp_tiles)),
    ("MULT18_R13C5", "MULT18_1", FuzzConfig(job="MULT18_1", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                             tiles=dsp_tiles)),
    ("MULT18_R13C8", "MULT18_4", FuzzConfig(job="MULT18_4", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                            tiles=dsp_tiles)),
    ("MULT18_R13C9", "MULT18_5", FuzzConfig(job="MULT18_5", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                            tiles=dsp_tiles)),
]


def main():
    pytrellis.load_database("../../../database")

    def per_job(job):
        def get_substs(settings, cibout="OFF", outclk="CLK0"):
            route = ""
            if cibout == "ON":
                if mult == "DSP_RIGHT" or mult == "MULT18_4":
                    route = "route\n\t\t\t" + rc + "_JP0_MULT18." + rc + "_JF4;"
                elif mult == "MULT18_1":
                    route = "route\n\t\t\t" + rc + "_JP0_MULT18.R13C4_JQ0;"
                elif mult == "MULT18_5":
                    route = "route\n\t\t\t" + rc + "_JP0_MULT18.R13C8_JQ4;"
                else:
                    route = "route\n\t\t\t" + rc + "_JP0_MULT18." + rc + "_JF0;"
            return dict(loc=loc, route=route, rc=rc, outclk=outclk)

        loc, mult, cfg = job
        rc = loc.split("_")[1]
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "dspconfig.ncl"
        if mult.startswith("MULT"):
            nonrouting.fuzz_enum_setting(cfg, "{}.CIBOUT_BYP".format(mult), ["OFF", "ON"],
                                     lambda x: get_substs(settings={}, cibout="ON", outclk=("NONE" if x == "ON" else "CLK0")), empty_bitfile, False)
        else:
            nonrouting.fuzz_enum_setting(cfg, "{}.CIBOUT".format(mult), ["OFF", "ON"],
                                     lambda x: get_substs(settings={}, cibout=x), empty_bitfile, False)

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
