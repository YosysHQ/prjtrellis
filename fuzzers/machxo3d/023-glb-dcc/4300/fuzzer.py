from fuzzconfig import FuzzConfig
import interconnect
import pytrellis
import nonrouting

jobs = [
    (FuzzConfig(job="GLB_DCC", family="MachXO3D", device="LCMXO3D-4300HC", ncl="empty.ncl",
                          tiles=["CENTER11:CENTER_EBR_CIB_4K", "CENTER_EBR24:CENTER_EBR",
                                 "CENTER14:CENTER8", "CENTER13:CENTER7", "CENTER12:CENTER6",
                                 "CENTER9:CENTERB", "CENTER10:CENTERC"]), 8)
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
