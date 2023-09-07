from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import argparse

jobs = [
    {
        "cfg": FuzzConfig(job="IOLOGIC_T0", family="MachXO2", device="LCMXO2-1200HC", ncl="empty_1200.ncl",
                          tiles=["PT11:PIC_T0"]),
        "side": "T",
        "sites": [("IOL_T11A", "A", "133"), ("IOL_T11B", "B", "132"), ("IOL_T11C", "C", "131"), ("IOL_T11D", "D", "130")],
        "ncl": "iologic_1200.ncl"
    },
]

def main(args):
    pytrellis.load_database("../../../database")

    for job in [jobs[i] for i in args.ids]:

        cfg = job["cfg"]
        side = job["side"]
        sites = job["sites"]

        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = job["ncl"]

        def per_site(site):
            loc, iol, pin = site

            def get_substs(mode=""):
                if mode != "NONE":
                    mode = "ODDR4:::LVDS71={}".format(mode)
                else:
                    mode = ""
                return dict(loc=loc, mode=mode)

            nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.ODDR4.LVDS71".format(iol), ["NONE", "YES", "NO"],
                                        lambda x: get_substs(mode=x), empty_bitfile, False)
    fuzzloops.parallel_foreach(sites, per_site)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IO ODDR4 LVDS71 Attributes Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
