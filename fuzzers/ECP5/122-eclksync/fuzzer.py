from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

jobs = [(FuzzConfig(job="ECLKSYNC0_BK6", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C2:ECLK_L"]), "ECLKSYNC0_BK6"),
        (FuzzConfig(job="ECLKSYNC1_BK6", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C2:ECLK_L"]), "ECLKSYNC1_BK6"),

        (FuzzConfig(job="ECLKSYNC0_BK7", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C2:ECLK_L"]), "ECLKSYNC0_BK7"),
        (FuzzConfig(job="ECLKSYNC1_BK7", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C2:ECLK_L"]), "ECLKSYNC1_BK7"),

        (FuzzConfig(job="ECLKSYNC0_BK3", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C88:ECLK_R"]), "ECLKSYNC0_BK3"),
        (FuzzConfig(job="ECLKSYNC1_BK3", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C88:ECLK_R"]), "ECLKSYNC1_BK3"),
        (FuzzConfig(job="ECLKSYNC0_BK2", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C88:ECLK_R"]), "ECLKSYNC0_BK2"),
        (FuzzConfig(job="ECLKSYNC1_BK2", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C88:ECLK_R"]), "ECLKSYNC1_BK2")
        ]


def main():
    pytrellis.load_database("../../../database")

    def per_job(job):

        def get_substs(mode="ECLKSYNCB"):
            if mode == "NONE":
                comment = "//"
            else:
                comment = ""
            return dict(site=loc, comment=comment)

        cfg, loc = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "eclksync.ncl"

        nonrouting.fuzz_enum_setting(cfg, "{}.MODE".format(loc), ["NONE", "ECLKSYNCB"],
                                     lambda x: get_substs(mode=x), empty_bitfile, False)



    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
