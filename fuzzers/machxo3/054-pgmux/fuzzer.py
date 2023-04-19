from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import argparse

jobs = [
        {
            "cfg": FuzzConfig(job="PIC_T0", family="MachXO3", device="LCMXO3LF-6900C",
                        ncl="empty_6900.ncl", tiles=["PT26:PIC_T0"]),
            "side": "T",
            "pins": [("A14", "A"), ("B14", "B"), ("D12", "C"), ("C12", "D")],
            "package": "CABGA400",
            "ncl": "pio_6900.ncl"
        },

        {
            "cfg": FuzzConfig(job="PIC_B0", family="MachXO3", device="LCMXO3LF-6900C",
                        ncl="empty_6900.ncl", tiles=["PB26:PIC_B0"]),
            "side": "B",
            "pins": [("Y13", "A"), ("W13", "B"), ("V12", "C"), ("V13", "D")],
            "package": "CABGA400",
            "ncl": "pio_6900.ncl"
        },

        {
            "cfg": FuzzConfig(job="PIC_L0", family="MachXO3", device="LCMXO3LF-1300E",
                        ncl="empty_1300.ncl", tiles=["PL8:PIC_L0"]),
            "side": "L",
            "pins": [("G11", "A"), ("G10", "B"), ("G9", "C"), ("G8", "D")],
            "package": "CSFBGA121",
            "ncl": "pio_1300.ncl"
        },

        {
            "cfg": FuzzConfig(job="PIC_R0", family="MachXO3", device="LCMXO3LF-1300E",
                        ncl="empty_1300.ncl", tiles=["PR8:PIC_R0"]),
            "side": "R",
            "pins": [("G1", "A"), ("G2", "B"), ("G3", "C"), ("G4", "D")],
            "package": "CSFBGA121",
            "ncl": "pio_1300.ncl"
        },
        #4
        {
            "cfg": FuzzConfig(job="ULC3PIC", family="MachXO3", device="LCMXO3LF-2100C",
                        ncl="empty_2100.ncl", tiles=["PL1:ULC3PIC"]),
            "side": "L",
            "pins": [("D3", "A"), ("D1", "B"), ("B1", "C"), ("C2", "D")],
            "package": "CABGA256",
            "ncl": "pio_2100.ncl"
        },
        {
            "cfg": FuzzConfig(job="URC1PIC", family="MachXO3", device="LCMXO3LF-2100C",
                        ncl="empty_2100.ncl", tiles=["PR1:URC1PIC"]),
            "side": "R",
            "pins": [("D14", "A"), ("E15", "B"), ("C15", "C"), ("B16", "D")],
            "package": "CABGA256",
            "ncl": "pio_2100.ncl"
        },
]

def main(args):
    pytrellis.load_database("../../../database")

    for job in [jobs[i] for i in args.ids]:

        cfg = job["cfg"]
        side = job["side"]
        pins = job["pins"]

        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = job["ncl"]

        def per_pin(pin):
            loc, pio = pin

            def get_substs(pgmux):
                return dict(loc=loc, pgmux=pgmux)

            nonrouting.fuzz_enum_setting(cfg, "PIO{}.PGMUX".format(pio), ["PGBUF", "INBUF"],
                                        lambda x: get_substs(pgmux=x), empty_bitfile, False)

        fuzzloops.parallel_foreach(pins, per_pin)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IO PGMUX Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
