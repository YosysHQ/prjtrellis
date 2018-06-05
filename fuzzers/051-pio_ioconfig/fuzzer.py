from fuzzconfig import FuzzConfig
import nonrouting
import nets
import pytrellis
import re
import fuzzloops


cfg = FuzzConfig(job="PIOCONFIG", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                 tiles=["MIB_R47C0:PICL0", "MIB_R48C0:PICL1", "MIB_R49C0:PICL2"])

pins = [("P4", "A"), ("P5", "B"), ("P6", "C"), ("P7", "D")]


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
            "LVCMOS18D"
        ]
        if dir == "INPUT":
            types += [
                "LVDS",
                "BLVDS25",
                "MLVDS25",
                "LVPECL33",
                "SLVS",
                "SUBLVDS"
            ]
        elif dir == "OUTPUT":
            if pio == "A":
                types += ["LVDS"]
            types += [
                "LVDS25E",
                "BLVDS25E",
                "MLVDS25E",
                "LVPECL33E",
            ]
        elif dir == "BIDIR":
            if pio == "A":
                types += ["LVDS"]
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

        modes = []
        for iodir in ("INPUT", "OUTPUT", "BIDIR"):
            modes += [iodir + "_" + _ for _ in get_io_types(iodir, pio, side)]

        nonrouting.fuzz_enum_setting(cfg, "PIO{}.TYPE".format(pio), modes,
                                     lambda x: get_substs(iomode=x),
                                     empty_bitfile)

    fuzzloops.parallel_foreach(pins, per_pin)


if __name__ == "__main__":
    main()
