from collections import defaultdict

from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re
import argparse
import fuzzloops
import nonrouting
import os
import sys

jobs = [
        {
            "cfg": FuzzConfig(job="PIC_T0", family="MachXO3", device="LCMXO3LF-6900C",
                        ncl="empty_6900.ncl", tiles=["PT26:PIC_T0"]),
            "side": "T",
            "pins": [("A14", "A"), ("B14", "B"), ("D12", "C"), ("C12", "D")],
            "package": "CABGA400"
        },

        {
            "cfg": FuzzConfig(job="PIC_B0", family="MachXO3", device="LCMXO3LF-6900C",
                        ncl="empty_6900.ncl", tiles=["PB26:PIC_B0"]),
            "side": "B",
            "pins": [("Y13", "A"), ("W13", "B"), ("V12", "C"), ("V13", "D")],
            "package": "CABGA400"
        },

        {
            "cfg": FuzzConfig(job="PIC_L0", family="MachXO3", device="LCMXO3LF-1300E",
                        ncl="empty_1300.ncl", tiles=["PL8:PIC_L0"]),
            "side": "L",
            "pins": [("G11", "A"), ("G10", "B"), ("G9", "C"), ("G8", "D")],
            "package": "CSFBGA121"
        },

        {
            "cfg": FuzzConfig(job="PIC_R0", family="MachXO3", device="LCMXO3LF-1300E",
                        ncl="empty_1300.ncl", tiles=["PR8:PIC_R0"]),
            "side": "R",
            "pins": [("G1", "A"), ("G2", "B"), ("G3", "C"), ("G4", "D")],
            "package": "CSFBGA121"
        },
        #4

        {
            "cfg": FuzzConfig(job="PIC_RS0", family="MachXO3", device="LCMXO3LF-1300E",
                        ncl="empty_1300.ncl", tiles=["PR3:PIC_RS0"]),
            "side": "R",
            "pins": [("D2", "A"), ("D1", "B")],
            "package": "CSFBGA121"
        },

        {
            "cfg": FuzzConfig(job="PIC_LS0", family="MachXO3", device="LCMXO3LF-1300E",
                        ncl="empty_1300.ncl", tiles=["PL9:PIC_LS0"]),
            "side": "L",
            "pins": [("H11", "A"), ("H10", "B")],
            "package": "CSFBGA121"
        },


        {
            "cfg": FuzzConfig(job="PIC_L2", family="MachXO3", device="LCMXO3LF-6900C",
                        ncl="empty_6900.ncl", tiles=["PL7:PIC_L2"]),
            "side": "L",
            "pins": [("G4", "A"), ("G3", "B"), ("H3", "C"), ("H4", "D")],
            "package": "CABGA400"
        },

        {
            "cfg": FuzzConfig(job="PIC_R1", family="MachXO3", device="LCMXO3LF-6900C",
                        ncl="empty_6900.ncl", tiles=["PR15:PIC_R1"]),
            "side": "R",
            "pins": [("L19", "A"), ("L20", "B"), ("L14", "C"), ("L15", "D")],
            "package": "CABGA400"
        },
        #8
        {
            "cfg": FuzzConfig(job="PIC_L1", family="MachXO3", device="LCMXO3LF-4300C",
                        ncl="empty_4300.ncl", tiles=["PL13:PIC_L1"]),
            "side": "L",
            "pins": [("J2", "A"), ("K1", "B"), ("H5", "C"), ("J4", "D")],
            "package": "CABGA256"
        },
        {
            "cfg": FuzzConfig(job="PIC_L3", family="MachXO3", device="LCMXO3LF-2100C",
                        ncl="empty_2100.ncl", tiles=["PL13:PIC_L3"]),
            "side": "L",
            "pins": [("M3", "A"), ("N1", "B"), ("N2", "C"), ("P1", "D")],
            "package": "CABGA256"
        },

        {
            "cfg": FuzzConfig(job="PIC_L0_VREF3", family="MachXO3", device="LCMXO3LF-1300E",
                        ncl="empty_1300.ncl", tiles=["PL4:PIC_L0_VREF3"]),
            "side": "L",
            "pins": [("D10", "A"), ("D11", "B"), ("E10", "C"), ("E11", "D")],
            "package": "CSFBGA121"
        },

        {
            "cfg": FuzzConfig(job="PIC_L0_VREF4", family="MachXO3", device="LCMXO3LF-9400C",
                        ncl="empty_9400.ncl", tiles=["PL12:PIC_L0_VREF4"]),
            "side": "L",
            "pins": [("J2", "A"), ("J1", "B"), ("K7", "C"), ("K6", "D")],
            "package": "CABGA484"
        },
        #12
        {
            "cfg": FuzzConfig(job="PIC_L0_VREF5", family="MachXO3", device="LCMXO3LF-9400C",
                        ncl="empty_9400.ncl", tiles=["PL2:PIC_L0_VREF5"]),
            "side": "L",
            "pins": [("D3", "A"), ("D4", "B"), ("F6", "C"), ("G7", "D")],
            "package": "CABGA484"
        },

        {
            "cfg": FuzzConfig(job="PIC_L1_VREF4", family="MachXO3", device="LCMXO3LF-4300C",
                        ncl="empty_4300.ncl", tiles=["PL8:PIC_L1_VREF4"]),
            "side": "L",
            "pins": [("H2", "A"), ("H1", "B"), ("H6", "C"), ("J1", "D")],
            "package": "CABGA324"
        },
        {
            "cfg": FuzzConfig(job="PIC_L1_VREF5", family="MachXO3", device="LCMXO3LF-4300C",
                        ncl="empty_4300.ncl", tiles=["PL2:PIC_L1_VREF5"]),
            "side": "L",
            "pins": [("B1", "A"), ("C2", "B"), ("D3", "C"), ("C1", "D")],
            "package": "CABGA324"
        },
        {
            "cfg": FuzzConfig(job="PIC_L2_VREF5", family="MachXO3", device="LCMXO3LF-6900C",
                        ncl="empty_6900.ncl", tiles=["PL2:PIC_L2_VREF5"]),
            "side": "L",
            "pins": [("C4", "A"), ("C3", "B"), ("F6", "C"), ("G6", "D")],
            "package": "CABGA400"
        },
        #16
        {
            "cfg": FuzzConfig(job="PIC_L2_VREF4", family="MachXO3", device="LCMXO3LF-6900C",
                        ncl="empty_6900.ncl", tiles=["PL12:PIC_L2_VREF4"]),
            "side": "L",
            "pins": [("L1", "A"), ("L2", "B"), ("L3", "C"), ("L4", "D")],
            "package": "CABGA400"
        },

        {
            "cfg": FuzzConfig(job="PIC_L3_VREF4", family="MachXO3", device="LCMXO3LF-2100C",
                        ncl="empty_2100.ncl", tiles=["PL5:PIC_L3_VREF4"]),
            "side": "L",
            "pins": [("E2", "A"), ("E3", "B"), ("C1", "C"), ("D2", "D")],
            "package": "CABGA256"
        },
        {
            "cfg": FuzzConfig(job="PIC_L3_VREF5", family="MachXO3", device="LCMXO3LF-2100C",
                        ncl="empty_2100.ncl", tiles=["PL2:PIC_L3_VREF5"]),
            "side": "L",
            "pins": [("B1", "A"), ("C2", "B"), ("D3", "C"), ("C1", "D")],
            "package": "CABGA256"
        },
]

# Function constructed from reading the MachXO3L sysIO Usage Guide.
# Diamond is very sensitive to invalid I/O combinations, and will happily
# change the I/O type out from under you if you give it a bad combination.
# This can lead to further errors when the Diamond-assigned I/O type is
# invalid for the pin (for the complementary pair, especially).
def get_io_types(dir, pio, side):
    # Singled-ended I/O types.
    types = [
        "LVTTL33",
        "LVCMOS33",
        "LVCMOS25",
        "LVCMOS18",
        "LVCMOS15",
        "LVCMOS12",
    ]

    if dir == "INPUT":
        types += [
            "LVCMOS25R33",
            "LVCMOS18R33",
            "LVCMOS18R25",
            "LVCMOS15R33",
            "LVCMOS15R25"
        ]

    if dir in ("INPUT", "BIDIR"):
        types += [
            "LVCMOS12R33",
            "LVCMOS12R25",
            "LVCMOS10R33",
            "LVCMOS10R25"
        ]

    # Differential I/O types.
    if pio in ("A", "C"):
        types += [
            "MIPI",
            "LVTTL33D",
            "LVCMOS33D",
            "LVCMOS25D",
            "LVCMOS18D",
        ]

        if dir == "INPUT":
            # True differential inputs.
            # FIXME: Also supported in bidir?
            # map_impl.mrp suggests no (warning: violates legal combination
            # and is ignored.)
            types += [
                "LVDS25",
                "LVPECL33",
                "MLVDS25",
                "BLVDS25"
            ]

        if dir == "OUTPUT":
            # Emulated differential output.
            # FIXME: Also supported in bidir?
            types += [
                "LVDS25E",
                "LVPECL33E",
                "MLVDS25E",
                "BLVDS25E"
            ]

            # True differential output. Only supported on Top and primary pair.
            if pio == "A" and side == "T":
                types += [
                    "LVDS25"
                ]
    return types


def get_cfg_vccio(iotype):
    m = re.match(r".*(\d)(\d)$", iotype)
    if m:
        return "{}.{}".format(m.group(1), m.group(2))
    m = re.match(r".*(\d)(\d)[ED]$", iotype)
    if m:
        return "{}.{}".format(m.group(1), m.group(2))
    if iotype == "MIPI":
        return "2.5"
    return "3.3"

def main(args):
    pytrellis.load_database("../../../database")
    for job in [jobs[i] for i in args.ids]:
        cfg = job["cfg"]
        side = job["side"]
        pins = job["pins"]

        os.environ['DEV_PACKAGE'] = job.get("package", "QFN32")

        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "pio.v"

        def per_pin(pin):
            loc, pio = pin

            def get_substs(iomode, extracfg=None):
                if iomode == "NONE":
                    iodir, type = "NONE", ""
                else:
                    iodir, type = iomode.split("_", 1)
                substs = {
                    "dir": iodir,
                    "io_type": type,
                    "loc": loc,
                    "extra_attrs": "",
                    "cfg_vio": "3.3"
                }
                if extracfg is not None:
                    substs["extra_attrs"] = '(* {}="{}" *)'.format(extracfg[0], extracfg[1])
                if side == "B":
                    substs["cfg_vio"] = get_cfg_vccio(type)
                return substs

            modes = ["NONE"]
            for iodir in ("INPUT", "OUTPUT", "BIDIR"):
                modes += [iodir + "_" + _ for _ in get_io_types(iodir, pio, side)]

            nonrouting.fuzz_enum_setting(cfg, "PIO{}.BASE_TYPE".format(pio), modes,
                                         lambda x: get_substs(iomode=x),
                                         empty_bitfile, False)

            nonrouting.fuzz_enum_setting(cfg, "PIO{}.PULLMODE".format(pio), ["UP", "DOWN", "NONE", "KEEPER"],
                                         lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("PULLMODE", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.SLEWRATE".format(pio), ["FAST", "SLOW"],
                                         lambda x: get_substs(iomode="OUTPUT_LVCMOS33", extracfg=("SLEWRATE", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.DRIVE".format(pio), ["2", "4", "6", "8", "12", "16"],
                                         lambda x: get_substs(iomode="OUTPUT_LVCMOS12" if x in ["2", "6"] else "OUTPUT_LVCMOS33", extracfg=("DRIVE", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.HYSTERESIS".format(pio), ["SMALL", "LARGE"],
                                         lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("HYSTERESIS", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.OPENDRAIN".format(pio), ["ON", "OFF"],
                                         lambda x: get_substs(iomode="OUTPUT_LVCMOS33", extracfg=("OPENDRAIN", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.CLAMP".format(pio), ["ON", "OFF"],
                                            lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("CLAMP", x)),
                                            empty_bitfile)
            if side in "B":
                nonrouting.fuzz_enum_setting(cfg, "PIO{}.DIFFRESISTOR".format(pio), ["OFF", "100"],
                                            lambda x: get_substs(iomode="INPUT_LVDS25", extracfg=("DIFFRESISTOR", x)),
                                            empty_bitfile)
            #if side in "T" and pio in "A":
            #    nonrouting.fuzz_enum_setting(cfg, "PIO{}.DIFFDRIVE".format(pio), ["3.5"],
            #                                 lambda x: get_substs(iomode="OUTPUT_LVDS25", extracfg=("DIFFDRIVE", x)),
            #                                 empty_bitfile)

        fuzzloops.parallel_foreach(pins, per_pin)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PIO Attributes Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
