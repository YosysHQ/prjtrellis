from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

jobs = [(FuzzConfig(job="ECLKBRIDGECS1", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C2:ECLK_L"]), "ECLKBRIDGECS1"),
        (FuzzConfig(job="ECLKBRIDGECS0", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C88:ECLK_R"]), "ECLKBRIDGECS0")
        ]


def main():
    pytrellis.load_database("../../../database")

    def per_job(job):

        def get_substs(mode="ECLKBRIDGECS"):
            if mode == "NONE":
                comment = "//"
            else:
                comment = ""
            return dict(site=loc, comment=comment)

        cfg, loc = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "eclkbridge.ncl"

        nonrouting.fuzz_enum_setting(cfg, "{}.MODE".format(loc), ["NONE", "ECLKBRIDGECS"],
                                     lambda x: get_substs(mode=x), empty_bitfile, False)



    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
