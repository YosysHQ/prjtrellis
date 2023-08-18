from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import argparse

jobs = [
    # 0
    {
        "cfg": FuzzConfig(job="IOLOGIC_L0", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty_9400.ncl",
                          tiles=["PL13:PIC_L0"]),
        "side": "L",
        "sites": [("IOL_L13A", "A", "G1"),("IOL_L13B", "B", "H2"),("IOL_L13C", "C", "H4"),("IOL_L13D", "D", "J6")],
        "ncl": "iologic_9400.ncl"
    },

    {
        "cfg": FuzzConfig(job="IOLOGIC_R1", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty_9400.ncl",
                          tiles=["PR16:PIC_R1"]),
        "side": "R",
        "sites": [("IOL_R16A", "A", "G16"),("IOL_R16B", "B", "H15"),("IOL_R16C", "C", "H13"),("IOL_R16D", "D", "J12")],
        "ncl": "iologic_9400.ncl"
    },

    {
        "cfg": FuzzConfig(job="IOLOGIC_T0", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty_9400.ncl",
                          tiles=["PT15:PIC_T0"]),
        "side": "T",
        "sites": [("IOL_T15A", "A", "D6"), ("IOL_T15B", "B", "E7"), ("IOL_T15C", "C", "C6"), ("IOL_T15D", "D", "A6")],
        "ncl": "iologic_9400.ncl"
    },
    {
        "cfg": FuzzConfig(job="IOLOGIC_B0", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty_9400.ncl",
                          tiles=["PB18:PIC_B0"]),
        "side": "B",
        "sites": [("IOL_B18A", "A", "R7"), ("IOL_B18B", "B", "P7"), ("IOL_B18C", "C", "M7"), ("IOL_B18D", "D", "N7")],
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

            def get_substs(settings={}, program={}, route=""):
                delay = "DELAY::::" + ",".join(["{}={}".format(k, v) for k, v in settings.items()])
                program = " ".join(["{}:{}".format(k, v) for k, v in program.items()])
                if side == "L":
                    s = ""
                else:
                    if iol in ("B", "D"):
                        s = ""
                    else:
                        if iol == "A":
                            s = side
                        else:
                            if side == "R":
                                s = side
                            else:
                                s = side + "S"
                return dict(loc=loc, delay=delay, program=program, route=route, s=s)

            nonrouting.fuzz_word_setting(cfg, "IOLOGIC{}.DELAY.DEL_VALUE".format(iol), 5 ,
                                        lambda x: get_substs(settings={
                                            "DEL0": str(1 if x[0] else 0),
                                            "DEL1": str(1 if x[1] else 0),
                                            "DEL2": str(1 if x[2] else 0),
                                            "DEL3": str(1 if x[3] else 0),
                                            "DEL4": str(1 if x[4] else 0)
                                            }),
                                        empty_bitfile)

        fuzzloops.parallel_foreach(sites, per_site)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IO LOGIC Delay Attributes Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
