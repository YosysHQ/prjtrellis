from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import argparse

jobs = [
    {
        "cfg": FuzzConfig(job="IOLOGIC_T0", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty_9400.ncl",
                          tiles=["PT15:PIC_T0"]),
        "side": "T",
        "sites": [("IOL_T15A", "A", "D6"), ("IOL_T15B", "B", "E7"), ("IOL_T15C", "C", "C6"), ("IOL_T15D", "D", "A6")],
        "ncl": "iologic_9400.ncl"
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
