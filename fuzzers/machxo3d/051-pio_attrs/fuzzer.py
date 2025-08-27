from collections import defaultdict

from fuzzconfig import FuzzConfig
import pytrellis
import re
import argparse
import fuzzloops
import nonrouting
import os

jobs = [
        {
            "cfg": FuzzConfig(job="PIC_T0", family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="empty_9400.ncl", tiles=["PT28:PIC_T0"]),
            "side": "T",
            "pins": [("G12", "A"), ("F12", "B"), ("E13", "C"), ("F13", "D")],
            "package": "CABGA484",
            "i3c": False
        },

        {
            "cfg": FuzzConfig(job="PIC_B0", family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="empty_9400.ncl", tiles=["PB27:PIC_B0"]),
            "side": "B",
            "pins": [("Y12", "A"), ("T12", "B"), ("U12", "C"), ("V12", "D")],
            "package": "CABGA484",
            "i3c": False
        },

        {
            "cfg": FuzzConfig(job="PIC_L0",  family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="empty_9400.ncl", tiles=["PL20:PIC_L0"]),
            "side": "L",
            "pins": [("P4", "A"), ("N5", "B"), ("N6", "C"), ("N7", "D")],
            "package": "CABGA484",
            "i3c": False
        },

        {
            "cfg": FuzzConfig(job="PIC_R1",  family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="empty_9400.ncl", tiles=["PR5:PIC_R1"]),
            "side": "R",
            "pins": [("F22", "A"), ("G22", "B"), ("F18", "C"), ("F19", "D")],
            "package": "CABGA484",
            "i3c": False
        },

        {
            "cfg": FuzzConfig(job="PIC_L0_I3C",  family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="empty_9400.ncl", tiles=["PL25:PIC_L0_I3C"]),
            "side": "L",
            "pins": [("T2", "A"), ("U1", "B"), ("R6", "C"), ("R7", "D")],
            "package": "CABGA484",
            "i3c": True
        },
]

# Function constructed from reading the MachXO3L sysIO Usage Guide.
# Diamond is very sensitive to invalid I/O combinations, and will happily
# change the I/O type out from under you if you give it a bad combination.
# This can lead to further errors when the Diamond-assigned I/O type is
# invalid for the pin (for the complementary pair, especially).
def get_io_types(dir, pio, side, i3c):
    # Singled-ended I/O types.
    types = [
        "LVTTL33",
        "LVCMOS33",
        "LVCMOS25",
        "LVCMOS18",
        "LVCMOS15",
        "LVCMOS12",
    ]

    #if i3c:
        #types += [
        #    "I3C33",
        #    "I3C18",
        #    "I3C12",
        #]

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
        i3c = job["i3c"]

        os.environ['DEV_PACKAGE'] = job.get("package", "CABGA484")

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
                    substs["extra_attrs"] = '(* CLAMP="OFF", PULLMODE="DOWN", OPENDRAIN="OFF", SLEWRATE="SLOW" *)'
                if side == "B":
                    substs["cfg_vio"] = get_cfg_vccio(type)
                return substs

            modes = ["NONE"]
            for iodir in ("INPUT", "OUTPUT", "BIDIR"):
                modes += [iodir + "_" + _ for _ in get_io_types(iodir, pio, side, i3c)]

            nonrouting.fuzz_enum_setting(cfg, "PIO{}.BASE_TYPE".format(pio), modes,
                                         lambda x: get_substs(iomode=x),
                                         empty_bitfile, False)

            nonrouting.fuzz_enum_setting(cfg, "PIO{}.PULLMODE".format(pio), ["I3C", "UP", "DOWN", "NONE", "KEEPER"],
                                         lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("PULLMODE", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.SLEWRATE".format(pio), ["FAST", "SLOW"],
                                         lambda x: get_substs(iomode="OUTPUT_LVCMOS33", extracfg=("SLEWRATE", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.DRIVE".format(pio), ["2", "4", "6", "8", "12", "16"],
                                         lambda x: get_substs(iomode="OUTPUT_LVCMOS12" if x in ["2", "6"] else "OUTPUT_LVCMOS33", extracfg=("DRIVE", x)))
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.HYSTERESIS".format(pio), ["SMALL", "LARGE"],
                                         lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("HYSTERESIS", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.OPENDRAIN".format(pio), ["ON", "OFF"],
                                         lambda x: get_substs(iomode="OUTPUT_LVCMOS33", extracfg=("OPENDRAIN", x)))
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.CLAMP".format(pio), ["ON", "OFF"],
                                            lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("CLAMP", x)),
                                            empty_bitfile)
            if side in "B" and pio in ["A", "C"]:
                nonrouting.fuzz_enum_setting(cfg, "PIO{}.DIFFRESISTOR".format(pio), ["OFF", "100"],
                                            lambda x: get_substs(iomode="INPUT_LVDS25", extracfg=("DIFFRESISTOR", x)))
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
