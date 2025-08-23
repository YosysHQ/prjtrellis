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
            "cfg": FuzzConfig(job="PIC_T0", family="MachXO2", device="LCMXO2-7000HC",
                        ncl="empty_7000.ncl", tiles=["PT26:PIC_T0"]),
            "side": "T",
            "pins": [("D12", "A"), ("E12", "B"), ("B15", "C"), ("C15", "D")],
            "package": "FPBGA484"
        },

        {
            "cfg": FuzzConfig(job="PIC_B0", family="MachXO2", device="LCMXO2-7000HC",
                        ncl="empty_7000.ncl", tiles=["PB26:PIC_B0"]),
            "side": "B",
            "pins": [("Y14", "A"), ("AB15", "B"), ("W12", "C"), ("V12", "D")],
            "package": "FPBGA484"
        },

        {
            "cfg": FuzzConfig(job="PIC_L0", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="empty_1200.ncl", tiles=["PL8:PIC_L0"]),
            "side": "L",
            "pins": [("23", "A"), ("24", "B"), ("25", "C"), ("26", "D")],
            "package": "TQFP144"
        },

        {
            "cfg": FuzzConfig(job="PIC_R0", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="empty_1200.ncl", tiles=["PR8:PIC_R0"]),
            "side": "R",
            "pins": [("86", "A"), ("85", "B"), ("84", "C"), ("83", "D")],
            "package": "TQFP144"
        },
        #4
        {
            "cfg": FuzzConfig(job="ULC3PIC", family="MachXO2", device="LCMXO2-2000HC",
                        ncl="empty_2000.ncl", tiles=["PL1:ULC3PIC"]),
            "side": "L",
            "pins": [("D3", "A"), ("D1", "B"), ("B1", "C"), ("C2", "D")],
            "package": "CABGA256"
        },
        {
            "cfg": FuzzConfig(job="URC1PIC", family="MachXO2", device="LCMXO2-2000HC",
                        ncl="empty_2000.ncl", tiles=["PR1:URC1PIC"]),
            "side": "R",
            "pins": [("D14", "A"), ("E15", "B"), ("C15", "C"), ("B16", "D")],
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
        "SSTL25_I",
        "SSTL18_I",
        "HSTL18_I"
    ]

    if dir == "INPUT":
        types += [
            "SSTL25_II",
            "SSTL18_II",
            "HSTL18_II",
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

    if side == "B":
        # Only bottom bank supports PCI33.
        types += [
            "PCI33"
        ]

    # Differential I/O types.
    if pio in ("A", "C"):
        types += [
            "SSTL25D_I",
            "SSTL18D_I",
            "HSTL18D_I",
            "MIPI",
            "LVTTL33D",
            "LVCMOS33D",
            "LVCMOS25D",
            "LVCMOS18D",
            "LVCMOS15D",
            "LVCMOS12D",
        ]

        if dir == "INPUT":
            # True differential inputs.
            # FIXME: Also supported in bidir?
            # map_impl.mrp suggests no (warning: violates legal combination
            # and is ignored.)
            types += [
                "SSTL25D_II",
                "SSTL18D_II",
                "HSTL18D_II",
                "LVDS25",
                "LVPECL33",
                "MLVDS25",
                "BLVDS25",
                "RSDS25"
            ]

        if dir == "OUTPUT":
            # Emulated differential output.
            # FIXME: Also supported in bidir?
            types += [
                "LVDS25E",
                "LVPECL33E",
                "MLVDS25E",
                "BLVDS25E",
                "RSDS25E"
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
                else:
                    substs["extra_attrs"] = '(* CLAMP="OFF", PULLMODE="FAILSAFE", OPENDRAIN="OFF" *)'
                if side == "B":
                    substs["cfg_vio"] = get_cfg_vccio(type)
                return substs

            modes = ["NONE"]
            for iodir in ("INPUT", "OUTPUT", "BIDIR"):
                modes += [iodir + "_" + _ for _ in get_io_types(iodir, pio, side)]

            nonrouting.fuzz_enum_setting(cfg, "PIO{}.BASE_TYPE".format(pio), modes,
                                         lambda x: get_substs(iomode=x),
                                         empty_bitfile, False)

            nonrouting.fuzz_enum_setting(cfg, "PIO{}.PULLMODE".format(pio), ["UP", "DOWN", "NONE", "KEEPER", "FAILSAFE"],
                                         lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("PULLMODE", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.SLEWRATE".format(pio), ["FAST", "SLOW"],
                                         lambda x: get_substs(iomode="OUTPUT_LVCMOS33", extracfg=("SLEWRATE", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.DRIVE".format(pio), ["2", "4", "6", "8", "12", "16", "24"],
                                         lambda x: get_substs(iomode="OUTPUT_LVCMOS12" if x in ["2", "6"] else "OUTPUT_LVCMOS33", extracfg=("DRIVE", x)))
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.HYSTERESIS".format(pio), ["SMALL", "LARGE"],
                                         lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("HYSTERESIS", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.OPENDRAIN".format(pio), ["ON", "OFF"],
                                         lambda x: get_substs(iomode="OUTPUT_LVCMOS33", extracfg=("OPENDRAIN", x)))
            if side in "B":
                nonrouting.fuzz_enum_setting(cfg, "PIO{}.CLAMP".format(pio), ["PCI", "OFF"],
                                             lambda x: get_substs(iomode="INPUT_PCI33", extracfg=("CLAMP", x)),
                                             empty_bitfile)
            else:
                nonrouting.fuzz_enum_setting(cfg, "PIO{}.CLAMP".format(pio), ["ON", "OFF"],
                                             lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("CLAMP", x)),
                                             empty_bitfile)
            #if side in "B":
            #    nonrouting.fuzz_enum_setting(cfg, "PIO{}.DIFFRESISTOR".format(pio), ["OFF", "100"],
            #                                lambda x: get_substs(iomode="INPUT_LVDS25", extracfg=("DIFFRESISTOR", x)),
            #                                empty_bitfile)
            if side in "T" and pio in "A":
                nonrouting.fuzz_enum_setting(cfg, "PIO{}.DIFFDRIVE".format(pio), ["1.25"],
                                             lambda x: get_substs(iomode="OUTPUT_LVDS25", extracfg=("DIFFDRIVE", x)),
                                             empty_bitfile)

        fuzzloops.parallel_foreach(pins, per_pin)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PIO Attributes Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
