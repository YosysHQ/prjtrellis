from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

jobs = [
    (FuzzConfig(job="DCCL", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                tiles=["MIB_R34C3:LMID_0"]), "L", 14),
    (FuzzConfig(job="DCCR", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                tiles=["MIB_R34C87:RMID_0"]), "R", 14),
    (FuzzConfig(job="DCCT", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                tiles=["MIB_R0C40:TMID_0", "MIB_R0C41:TMID_1"]), "T", 12),
    (FuzzConfig(job="DCCB", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                tiles=["MIB_R71C40:BMID_0V", "MIB_R71C41:BMID_2V"]), "B", 16),
]


def main():
    pytrellis.load_database("../../database")

    def per_job(job):
        cfg, side, N = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "dcc.ncl"
        for i in range(N):
            def get_substs(mode="DCCA"):
                if mode == "NONE":
                    comment = "//"
                else:
                    comment = ""
                return dict(site=loc, comment=comment)

            loc = "DCC_{}{}".format(side, i)
            nonrouting.fuzz_enum_setting(cfg, "{}.MODE".format(loc), ["NONE", "DCCA"],
                                         lambda x: get_substs(mode=x), empty_bitfile, False)

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
