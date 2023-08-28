from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import argparse

jobs = [
    # 0
    {
        "cfg": FuzzConfig(job="IOLOGIC_L0", family="MachXO2", device="LCMXO2-1200HC", ncl="empty_1200.ncl",
                          tiles=["PL3:PIC_L0"]),
        "side": "L",
        "sites": [("IOL_L3A", "A", "5"),("IOL_L3B", "B", "6"),("IOL_L3C", "C", "9"),("IOL_L3D", "D", "10")],
        "ncl": "iologic_1200.ncl"
    },

    {
        "cfg": FuzzConfig(job="IOLOGIC_R0", family="MachXO2", device="LCMXO2-1200HC", ncl="empty_1200.ncl",
                          tiles=["PR2:PIC_R0"]),
        "side": "R",
        "sites": [("IOL_R2A", "A", "107"),("IOL_R2B", "B", "106"),("IOL_R2C", "C", "105"),("IOL_R2D", "D", "104")],
        "ncl": "iologic_1200.ncl"
    },

    {
        "cfg": FuzzConfig(job="IOLOGIC_T0", family="MachXO2", device="LCMXO2-1200HC", ncl="empty_1200.ncl",
                          tiles=["PT11:PIC_T0"]),
        "side": "T",
        "sites": [("IOL_T11A", "A", "133"), ("IOL_T11B", "B", "132"), ("IOL_T11C", "C", "131"), ("IOL_T11D", "D", "130")],
        "ncl": "iologic_1200.ncl"
    },
    {
        "cfg": FuzzConfig(job="IOLOGIC_B0", family="MachXO2", device="LCMXO2-1200HC", ncl="empty_1200.ncl",
                          tiles=["PB18:PIC_B0"]),
        "side": "B",
        "sites": [("IOL_B18A", "A", "61"), ("IOL_B18B", "B", "62"), ("IOL_B18C", "C", "65"), ("IOL_B18D", "D", "67")],
        "ncl": "iologic_1200.ncl"
    },
    #4
    {
        "cfg": FuzzConfig(job="IOLOGIC_ULC3PIC", family="MachXO2", device="LCMXO2-2000HC", ncl="empty_2000.ncl",
                          tiles=["PL1:ULC3PIC"]),
        "side": "L",
        "sites": [("IOL_L1A", "A", "D3"), ("IOL_L1B", "B", "D1"), ("IOL_L1C", "C", "B1"), ("IOL_L1D", "D", "C2")],
        "ncl": "iologic_2000.ncl"
    },
    {
        "cfg": FuzzConfig(job="IOLOGIC_ULC3PIC", family="MachXO2", device="LCMXO2-2000HC", ncl="empty_2000.ncl",
                          tiles=["PR1:URC1PIC"]),
        "side": "R",
        "sites": [("IOL_R1A", "A", "D14"), ("IOL_R1B", "B", "E15"), ("IOL_R1C", "C", "C15"), ("IOL_R1D", "D", "B16")],
        "ncl": "iologic_2000.ncl"
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
