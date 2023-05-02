from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import argparse

jobs = [
        {
            "cfg": FuzzConfig(job="PIC_T0", family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="empty_9400.ncl", tiles=["PT28:PIC_T0"]),
            "side": "T",
            "pins": [("G12", "A"), ("F12", "B"), ("E13", "C"), ("F13", "D")],
            "package": "CABGA484",
            "ncl": "pio_9400.ncl"
        },

        {
            "cfg": FuzzConfig(job="PIC_B0", family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="empty_9400.ncl", tiles=["PB27:PIC_B0"]),
            "side": "B",
            "pins": [("Y12", "A"), ("T12", "B"), ("U12", "C"), ("V12", "D")],
            "package": "CABGA484",
            "ncl": "pio_9400.ncl"
        },

        {
            "cfg": FuzzConfig(job="PIC_L0", family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="empty_9400.ncl", tiles=["PL20:PIC_L0"]),
            "side": "L",
            "pins": [("P4", "A"), ("N5", "B"), ("N6", "C"), ("N7", "D")],
            "package": "CABGA484",
            "ncl": "pio_9400.ncl"
        },

        {
            "cfg": FuzzConfig(job="PIC_R0", family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="empty_9400.ncl", tiles=["PR5:PIC_R1"]),
            "side": "R",
            "pins": [("F22", "A"), ("G22", "B"), ("F18", "C"), ("F19", "D")],
            "package": "CABGA484",
            "ncl": "pio_9400.ncl"
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
