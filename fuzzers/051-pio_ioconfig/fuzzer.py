from fuzzconfig import FuzzConfig
import nonrouting
import nets
import pytrellis
import re
import fuzzloops

cfg = FuzzConfig(job="PIOCONFIG", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                 tiles=["MIB_R59C0:PICL0", "MIB_R60C0:PICL1", "MIB_R61C0:PICL2"])

pins = [("M4", "A"), ("N5", "B"), ("N4", "C"), ("P5", "D")]


def get_io_types(dir, pio, side):
    types = [
        "LVTTL33",
        "LVCMOS33",
        "LVCMOS25",
        "LVCMOS18",
        "LVCMOS15",
        "LVCMOS12"
    ]
    if side in ('L', 'R'):
        types += [
            "SSTL18_I",
            "SSTL18_II",
            "SSTL15_I",
            "SSTL15_II",
            "SSTL135_I",
            "SSTL135_II",
            "HSUL12"
        ]
    if pio in ('A', 'C') and side in ('L', 'R'):
        types += [
            "SSTL18D_I",
            "SSTL18D_II",
            "SSTL135D_I",
            "SSTL135D_II",
            "SSTL15D_I",
            "SSTL15D_II",
            "HSUL12D",
            "LVCMOS33D",
            "LVCMOS25D",
        ]
        if dir == "INPUT":
            types += [
                "LVDS",
                "BLVDS25",
                "MLVDS25",
                "LVPECL33",
                "SLVS",
                "SUBLVDS",
                "LVCMOS18D"
            ]
        elif dir == "OUTPUT":
            if pio == "A":
                types += ["LVDS", "LVCMOS18D"]
            types += [
                "LVDS25E",
                "BLVDS25E",
                "MLVDS25E",
                "LVPECL33E",
            ]
        elif dir == "BIDIR":
            if pio == "A":
                types += ["LVDS", "LVCMOS18D"]
            types += [
                "BLVDS25E",
                "MLVDS25E",
            ]
    return types


def main():
    pytrellis.load_database("../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "pio.v"
    side = "L"

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
                "extra_attrs": ""
            }
            if extracfg is not None:
                substs["extra_attrs"] = '(* {}="{}" *)'.format(extracfg[0], extracfg[1])
            return substs

        modes = ["NONE"]
        for iodir in ("INPUT", "OUTPUT", "BIDIR"):
            modes += [iodir + "_" + _ for _ in get_io_types(iodir, pio, side)]

        nonrouting.fuzz_enum_setting(cfg, "PIO{}.BASE_TYPE".format(pio), modes,
                                     lambda x: get_substs(iomode=x),
                                     empty_bitfile, False)

        nonrouting.fuzz_enum_setting(cfg, "PIO{}.PULLMODE".format(pio), ["UP", "DOWN", "NONE"],
                                     lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("PULLMODE", x)),
                                     empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "PIO{}.SLEWRATE".format(pio), ["FAST", "SLOW"],
                                     lambda x: get_substs(iomode="OUTPUT_LVCMOS33", extracfg=("SLEWRATE", x)),
                                     empty_bitfile)
    fuzzloops.parallel_foreach(pins, per_pin)


if __name__ == "__main__":
    main()
