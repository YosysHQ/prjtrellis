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

            def get_substs(mode="IREG_OREG", program=[]):
                if mode == "NONE":
                    comment = "//"
                    program = ""
                else:
                    comment = ""
                    program = "program " + "\n\t\t\t".join(['"' + _ + ' "' for _ in program])
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
                return dict(loc=loc, mode=mode, program=program, comment=comment, side=s)

            modes = ["NONE", "IREG_OREG", "IDDR_ODDR"]
            if side in "B":
                if iol in ("A","C"):
                    modes += ["IDDR2"]
                if iol in ("A"):
                    modes += ["IDDR4"]
            if side in "T":
                if iol in ("A","C"):
                    modes += ["ODDR2"]
                if iol in ("A"):
                    modes += ["ODDR4"]
                
            tie_program = ["LSRIMUX:0", "LSROMUX:0", "CLKIMUX:0", "CLKOMUX:0" ]
            nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.MODE".format(iol), modes,
                                        lambda x: get_substs(mode=x, program=["MODE:" + x] + tie_program), empty_bitfile, False)

        fuzzloops.parallel_foreach(sites, per_site)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IO LOGIC Modes Attributes Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
