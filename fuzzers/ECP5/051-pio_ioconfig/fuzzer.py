from fuzzconfig import FuzzConfig
import nonrouting
import nets
import pytrellis
import re
import fuzzloops

jobs = [
    {
        "cfg": FuzzConfig(job="PIOL", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R59C0:PICL0", "MIB_R60C0:PICL1", "MIB_R61C0:PICL2"]),
        "side": "L",
        "pins": [("M4", "A"), ("N5", "B"), ("N4", "C"), ("P5", "D")]
    },
    {
        "cfg": FuzzConfig(job="PIOL_CLR", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R20C0:PICL0", "MIB_R21C0:PICL1", "MIB_R22C0:MIB_CIB_LR",
                                 "MIB_R22C0:MIB_CIB_LRC"]),
        "side": "L",
        "pins": [("F4", "A"), ("E3", "B"), ("E5", "C"), ("F5", "D")]
    },
    {
        "cfg": FuzzConfig(job="PIOL_DQS01", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R14C0:PICL0", "MIB_R15C0:PICL1_DQS0", "MIB_R16C0:PICL2_DQS1"]),
        "side": "L",
        "pins": [("C4", "A"), ("B4", "B"), ("A3", "C"), ("B3", "D")]
    },
    {
        "cfg": FuzzConfig(job="PIOL_DQS23", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R17C0:PICL0_DQS2", "MIB_R18C0:PICL1_DQS3", "MIB_R19C0:PICL2"]),
        "side": "L",
        "pins": [("E4", "A"), ("D5", "B"), ("C3", "C"), ("D3", "D")]
    },
    {
        "cfg": FuzzConfig(job="PIOR", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R35C90:PICR0", "MIB_R36C90:PICR1", "MIB_R37C90:PICR2"]),
        "side": "R",
        "pins": [("L20", "A"), ("M20", "B"), ("L19", "C"), ("M19", "D")]
    },
    {
        "cfg": FuzzConfig(job="PIOR_CLRA", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R32C90:PICR0", "MIB_R33C90:PICR1", "MIB_R34C90:MIB_CIB_LR_A",
                                 "MIB_R34C90:MIB_CIB_LRC_A"]),
        "side": "R",
        "pins": [("J19", "A"), ("K19", "B"), ("J20", "C"), ("K20", "D")]
    },
    {
        "cfg": FuzzConfig(job="PIOT", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R0C4:PIOT0", "MIB_R0C5:PIOT1", "MIB_R1C4:PICT0",
                                 "MIB_R1C5:PICT1"]),
        "side": "T",
        "pins": [("A6", "A"), ("B6", "B")]
    },
    {
        "cfg": FuzzConfig(job="PIOB", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R71C9:PICB0", "MIB_R71C10:PICB1"]),
        "side": "B",
        "pins": [("W1", "A"), ("Y2", "B")]
    },
    {
        "cfg": FuzzConfig(job="PIOB_EFB", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R71C6:EFB2_PICB0", "MIB_R71C7:EFB3_PICB1"]),
        "side": "B",
        "pins": [("U1", "A"), ("V1", "B")]
    },
    {
         "cfg": FuzzConfig(job="SPIOB", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                           tiles=["MIB_R71C18:SPICB0"]),
         "side": "B",
         "pins": [("T3", "A")]
    },
]


def get_io_types(dir, pio, side):
    types = [
        "LVTTL33",
        "LVCMOS33",
        "LVCMOS25",
        "LVCMOS18",
        "LVCMOS15",
        "LVCMOS12"
    ]
    if pio == "A" and side == "T" and dir == "OUTPUT":
        types += [
            "LVCMOS33D",
            "LVCMOS25D",
            "LVCMOS18D",
            "LVCMOS15D",
            "LVCMOS12D"
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


def get_cfg_vccio(iotype):
    m = re.match(r".*(\d)(\d)$", iotype)
    if not m:
        return "3.3"
    return "{}.{}".format(m.group(1), m.group(2))


def main():
    pytrellis.load_database("../../../database")
    for job in jobs:
        cfg = job["cfg"]
        side = job["side"]
        pins = job["pins"]
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
                    pullcfg = ""
                    if extracfg[0] == "CLAMP":
                        pullcfg = ", PULLMODE=\"UP\""
                    substs["extra_attrs"] = '(* {}="{}"{} *)'.format(extracfg[0], extracfg[1], pullcfg)
                if side == "B":
                    substs["cfg_vio"] = get_cfg_vccio(type)
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
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.DRIVE".format(pio), ["4", "8", "12", "16"],
                                         lambda x: get_substs(iomode="OUTPUT_LVCMOS33", extracfg=("DRIVE", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.HYSTERESIS".format(pio), ["ON", "OFF"],
                                         lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("HYSTERESIS", x)),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.OPENDRAIN".format(pio), ["ON", "OFF"],
                                         lambda x: get_substs(iomode="OUTPUT_LVCMOS33", extracfg=("OPENDRAIN", x)),
                                         empty_bitfile)
            if side in ('T', 'B'):
                nonrouting.fuzz_enum_setting(cfg, "PIO{}.CLAMP".format(pio), ["ON", "OFF"],
                                             lambda x: get_substs(iomode="INPUT_LVCMOS33", extracfg=("CLAMP", x)))

        fuzzloops.parallel_foreach(pins, per_pin)


if __name__ == "__main__":
    main()
