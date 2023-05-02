from fuzzconfig import FuzzConfig
import interconnect
import pytrellis
import nonrouting

jobs = [
    (FuzzConfig(job="GLB_DCC", family="MachXO3", device="LCMXO3LF-1300E", ncl="empty.ncl",
                          tiles=["CENTER6:CENTER_EBR_CIB", "CENTER_EBR14:CENTER_EBR",
                                 "CENTER9:CENTER8", "CENTER8:CENTER7", "CENTER7:CENTER6",
                                 "CENTER5:CENTER5", "CENTER4:CENTER4"]), 8)
]


def main():
    pytrellis.load_database("../../../../database")

    for job in jobs:
        cfg, N = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "dcc.ncl"
        for i in range(N):
            loc = "DCC{}".format(i)
            def get_substs(mode="DCCA"):
                if mode == "NONE":
                    comment = "//"
                else:
                    comment = ""
                return dict(site=loc, comment=comment)

            nonrouting.fuzz_enum_setting(cfg, "{}.MODE".format(loc), ["NONE", "DCCA"],
                                         lambda x: get_substs(mode=x), empty_bitfile, False)

if __name__ == "__main__":
    main()
