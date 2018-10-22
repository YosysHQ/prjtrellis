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
    ("MULT18_R13C4", "DSP_LEFT", FuzzConfig(job="MULT18_0", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                            tiles=dsp_tiles)),
    ("MULT18_R13C8", "DSP_RIGHT", FuzzConfig(job="MULT18_4", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                             tiles=dsp_tiles)),
]


def main():
    pytrellis.load_database("../../database")

    def per_job(job):
        def get_substs(settings, cibout="OFF"):
            route = ""
            if cibout == "ON":
                if mult == "DSP_RIGHT":
                    route = "route\n\t\t\t" + rc + "_JP0_MULT18." + rc + "_JF4;"
                else:
                    route = "route\n\t\t\t" + rc + "_JP0_MULT18." + rc + "_JF0;"
            return dict(loc=loc, route=route, rc=rc)

        loc, mult, cfg = job
        rc = loc.split("_")[1]
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "dspconfig.ncl"
        nonrouting.fuzz_enum_setting(cfg, "{}.CIBOUT".format(mult), ["OFF", "ON"],
                                     lambda x: get_substs(settings={}, cibout=x), empty_bitfile, False)

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
