from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

jobs = [(FuzzConfig(job="CLKDIVL0", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C2:ECLK_L"]), "CLKDIV_L0", "R34C0"),
        (FuzzConfig(job="CLKDIVL1", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C2:ECLK_L"]), "CLKDIV_L1", "R34C0"),
        (FuzzConfig(job="CLKDIVR0", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C88:ECLK_R"]), "CLKDIV_R0", "R34C90"),
        (FuzzConfig(job="CLKDIVR1", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C88:ECLK_R"]), "CLKDIV_R1", "R34C90")
        ]


def main():
    pytrellis.load_database("../../../database")

    def per_job(job):

        def get_substs(mode="CLKDIVF", div="2.0", gsr="ENABLED"):
            if mode == "NONE":
                comment = "//"
            else:
                comment = ""
            return dict(site=loc, comment=comment, div=div, gsr=gsr)

        cfg, loc, rc = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "clkdiv.ncl"

        nonrouting.fuzz_enum_setting(cfg, "{}.DIV".format(loc), ["2.0", "3.5"],
                                     lambda x: get_substs(div=x), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.GSR".format(loc), ["ENABLED", "DISABLED"],
                                     lambda x: get_substs(gsr=x), empty_bitfile)

        idx = loc[-1]
        nets = ["{}_JCDIVX_CLKDIV{}".format(rc, idx),
                "{}_CLKI_CLKDIV{}".format(rc, idx),
                "{}_JRST_CLKDIV{}".format(rc, idx),
                "{}_JALIGNWD_CLKDIV{}".format(rc, idx),
                "{}_CLKI{}".format(rc, idx),
                ]
        cfg.ncl = "clkdiv_routing.ncl"
        interconnect.fuzz_interconnect_with_netnames(cfg, nets, bidir=True)

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
