from fuzzconfig import FuzzConfig
import interconnect
import pytrellis
import nonrouting

jobs = [
    (FuzzConfig(job="GLB_DCC", family="MachXO3", device="LCMXO3LF-9400C", ncl="empty.ncl",
                          tiles=["CENTER15:CENTER_EBR_CIB_10K", "CENTER_EBR34:CENTER_EBR",
                                 "CENTER18:CENTER8", "CENTER17:CENTER7", "CENTER16:CENTER6",
                                 "CENTER13:CENTER9", "CENTER14:CENTERA"]), 8)
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
