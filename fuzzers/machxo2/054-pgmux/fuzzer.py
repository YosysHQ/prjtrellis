from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import argparse

jobs = [
        {
            "cfg": FuzzConfig(job="PIC_T0", family="MachXO2", device="LCMXO2-7000HC",
                        ncl="empty_7000.ncl", tiles=["PT26:PIC_T0"]),
            "side": "T",
            "pins": [("D12", "A"), ("E12", "B"), ("B15", "C"), ("C15", "D")],
            "package": "FPBGA484",
            "ncl": "pio_7000.ncl"
        },

        {
            "cfg": FuzzConfig(job="PIC_B0", family="MachXO2", device="LCMXO2-7000HC",
                        ncl="empty_7000.ncl", tiles=["PB26:PIC_B0"]),
            "side": "B",
            "pins": [("Y14", "A"), ("AB15", "B"), ("W12", "C"), ("V12", "D")],
            "package": "FPBGA484",
            "ncl": "pio_7000.ncl"
        },

        {
            "cfg": FuzzConfig(job="PIC_L0", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="empty_1200.ncl", tiles=["PL8:PIC_L0"]),
            "side": "L",
            "pins": [("23", "A"), ("24", "B"), ("25", "C"), ("26", "D")],
            "package": "TQFP144",
            "ncl": "pio_1200.ncl"
        },

        {
            "cfg": FuzzConfig(job="PIC_R0", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="empty_1200.ncl", tiles=["PR8:PIC_R0"]),
            "side": "R",
            "pins": [("86", "A"), ("85", "B"), ("84", "C"), ("83", "D")],
            "package": "TQFP144",
            "ncl": "pio_1200.ncl"
        },
        #4
        {
            "cfg": FuzzConfig(job="ULC3PIC", family="MachXO2", device="LCMXO2-2000HC",
                        ncl="empty_2000.ncl", tiles=["PL1:ULC3PIC"]),
            "side": "L",
            "pins": [("D3", "A"), ("D1", "B"), ("B1", "C"), ("C2", "D")],
            "package": "CABGA256",
            "ncl": "pio_2000.ncl"
        },
        {
            "cfg": FuzzConfig(job="URC1PIC", family="MachXO2", device="LCMXO2-2000HC",
                        ncl="empty_2000.ncl", tiles=["PR1:URC1PIC"]),
            "side": "R",
            "pins": [("D14", "A"), ("E15", "B"), ("C15", "C"), ("B16", "D")],
            "package": "CABGA256",
            "ncl": "pio_2000.ncl"
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
