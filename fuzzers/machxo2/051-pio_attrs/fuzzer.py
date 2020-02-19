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

jobs = [
        {
            "cfg": FuzzConfig(job="PICB0_AB", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="empty.ncl", tiles=["PB11:PIC_B0"]),
            "side": "B",
            "pins": [("13", "A"), ("14", "B")]
        },

        # Split into multiple jobs, because Diamond chokes if the I/Os don't
        # actually physically exist (QFN32 is default).
        {
            "cfg": FuzzConfig(job="PICB0_CD", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="empty.ncl", tiles=["PB6:PIC_B0"]),
            "side": "B",
            "pins": [("9", "C"), ("10", "D")]
        },

        {
            "cfg": FuzzConfig(job="PICL0_IO", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="empty.ncl", tiles=["PL5:PIC_L0"]),
            "side": "L",
            "pins": [("12", "A"), ("13", "B"), ("14", "C"), ("15", "D")],
            "package": "TQFP100"
        },

        {
            "cfg": FuzzConfig(job="PICR0_IO", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="empty.ncl", tiles=["PR5:PIC_R0"]),
            "side": "R",
            "pins": [("65", "A"), ("64", "B"), ("63", "C"), ("62", "D")],
            "package": "TQFP100"
        },

        {
            "cfg": FuzzConfig(job="PICT0_IO", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="empty.ncl", tiles=["PT10:PIC_T0"]),
            "side": "T",
            "pins": [("97", "A"), ("96", "B")],
            "package": "TQFP100"
        },

        # FIXME: WARNING - map: In "LOCATE COMP "pad" SITE "PT10{C,D} pin" ;":
        # Current SYS_CONFIG setting prohibits pin be used as user IO. This
        # preference has been disabled. Why?
        {
            "cfg": FuzzConfig(job="PICT0_IO", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="empty.ncl", tiles=["PT12:PIC_T0"]),
            "side": "T",
            "pins": [("28", "C"), ("27", "D")]
        },
]

# Function constructed from reading the MachXO2 sysIO Usage Guide.
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
    if not m:
        return "3.3"
    return "{}.{}".format(m.group(1), m.group(2))


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

            nonrouting.fuzz_enum_setting(cfg, "PIO{}.PULLMODE".format(pio), ["UP", "DOWN", "NONE", "KEEPER", "FAILSAFE"],
                                         lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("PULLMODE", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.SLEWRATE".format(pio), ["FAST", "SLOW"],
                                         lambda x: get_substs(iomode="OUTPUT_LVCMOS33", extracfg=("SLEWRATE", x)),
                                         empty_bitfile)
            # # FIXME: Do LVCMOS12, which is 2/6mA.
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.DRIVE".format(pio), ["4", "8", "12", "16", "24"],
                                         lambda x: get_substs(iomode="OUTPUT_LVCMOS33", extracfg=("DRIVE", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.HYSTERESIS".format(pio), ["SMALL", "LARGE"],
                                         lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("HYSTERESIS", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.OPENDRAIN".format(pio), ["ON", "OFF"],
                                         lambda x: get_substs(iomode="OUTPUT_LVCMOS33", extracfg=("OPENDRAIN", x)),
                                         empty_bitfile)
            if loc in "B":
                nonrouting.fuzz_enum_setting(cfg, "PIO{}.CLAMP".format(pio), ["PCI", "OFF"],
                                             lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("CLAMP", x)),
                                             empty_bitfile)
            else:
                nonrouting.fuzz_enum_setting(cfg, "PIO{}.CLAMP".format(pio), ["ON", "OFF"],
                                             lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("CLAMP", x)),
                                             empty_bitfile)
            if loc in "T" and pio in "A":
                nonrouting.fuzz_enum_setting(cfg, "PIO{}.DIFFDRIVE".format(pio), ["1.25", "2.0", "2.5", "3.5"],
                                             lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("CLAMP", x)),
                                             empty_bitfile)

        fuzzloops.parallel_foreach(pins, per_pin)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CIB_EBRn Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
