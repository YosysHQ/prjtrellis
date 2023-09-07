from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops

jobs = [
        (FuzzConfig(job="BCLKDIV0", family="MachXO2", device="LCMXO2-2000HC", ncl="empty.ncl",
                    tiles=["PB14:PIC_B_DUMMY_VIQ_VREF"]), "BCLKDIV0"),
        (FuzzConfig(job="BCLKDIV1", family="MachXO2", device="LCMXO2-2000HC", ncl="empty.ncl",
                    tiles=["PB14:PIC_B_DUMMY_VIQ_VREF"]), "BCLKDIV1"),
]

def main():
    pytrellis.load_database("../../../../database")

    def per_job(job):

        def get_substs(mode="CLKDIVC", div="2.0", gsr="ENABLED"):
            if mode == "NONE":
                comment = "//"
            else:
                comment = ""
            return dict(site=loc, comment=comment, div=div, gsr=gsr)

        cfg, loc = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "clkdiv.ncl"

        nonrouting.fuzz_enum_setting(cfg, "{}.DIV".format(loc), ["2.0", "3.5", "4.0"],
                                     lambda x: get_substs(div=x), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.GSR".format(loc), ["ENABLED", "DISABLED"],
                                     lambda x: get_substs(gsr=x), empty_bitfile)

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
