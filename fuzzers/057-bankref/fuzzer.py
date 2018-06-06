from fuzzconfig import FuzzConfig
import nonrouting
import nets
import pytrellis
import re
import fuzzloops

jobs = [
    # 45k
    {
        "cfg": FuzzConfig(job="BANKREF0", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R0C3:BANKREF0"]),
        "side": "T",
        "pin": "A6"
    },
    {
        "cfg": FuzzConfig(job="BANKREF1", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R0C87:BANKREF1"]),
        "side": "T",
        "pin": "A19"
    },
    {
        "cfg": FuzzConfig(job="BANKREF2", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R10C90:BANKREF2"]),
        "side": "R",
        "pin": "C18"
    },
    {
        "cfg": FuzzConfig(job="BANKREF3", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R71C89:BANKREF3"]),
        "side": "R",
        "pin": "N17"
    },
    {
        "cfg": FuzzConfig(job="BANKREF6", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R71C1:BANKREF6"]),
        "side": "L",
        "pin": "N3"
    },
    {
        "cfg": FuzzConfig(job="BANKREF7", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R10C0:BANKREF7"]),
        "side": "L",
        "pin": "F4"
    },
    {
        "cfg": FuzzConfig(job="BANKREF8", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R71C3:BANKREF8"]),
        "side": "B",
        "pin": "R1"
    },
    # 25k
    {
        "cfg": FuzzConfig(job="BANKREF7A", family="ECP5", device="LFE5U-25F", ncl="empty_25k.ncl",
                          tiles=["MIB_R1C0:BANKREF7A"]),
        "side": "L",
        "pin": "A4"
    },
    {
        "cfg": FuzzConfig(job="BANKREF2A", family="ECP5", device="LFE5U-25F", ncl="empty_25k.ncl",
                          tiles=["MIB_R1C72:BANKREF2A"]),
        "side": "R",
        "pin": "J19"
    },
    # 85k
    {
        "cfg": FuzzConfig(job="BANKREF4", family="ECP5", device="LFE5U-85F", ncl="empty_85k.ncl",
                          tiles=["MIB_R95C123:BANKREF4"]),
        "side": "B",
        "pin": "AJ29"
    },
]


def main():
    pytrellis.load_database("../../database")
    for job in jobs:
        cfg = job["cfg"]
        side = job["side"]
        pin = job["pin"]
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "pio.v"

        def get_substs(iomode, extracfg=None):
            if iomode == "NONE":
                iodir, type = "NONE", ""
            else:
                iodir, type = iomode.split("_", 1)
            substs = {
                "dir": iodir,
                "io_type": type,
                "loc": pin,
                "extra_attrs": ""
            }
            if extracfg is not None:
                substs["extra_attrs"] = '(* {}="{}" *)'.format(extracfg[0], extracfg[1])
            return substs

        vcco_opts = {
            "1V2": "OUTPUT_LVCMOS12",
            "1V5": "OUTPUT_LVCMOS15",
            "1V8": "OUTPUT_LVCMOS18",
            "2V5": "OUTPUT_LVCMOS25",
            "3V3": "OUTPUT_LVCMOS33",
            "NONE": "INPUT_LVCMOS12",
        }

        nonrouting.fuzz_enum_setting(cfg, "BANK.VCCIO", list(sorted(vcco_opts.keys())),
                                     lambda x: get_substs(iomode=vcco_opts[x]),
                                     empty_bitfile)
        if side in ('L', 'R'):
            nonrouting.fuzz_enum_setting(cfg, "BANK.DIFF", ["OFF", "ON"],
                                         lambda x: get_substs(
                                             iomode="OUTPUT_LVCMOS33D" if x == "ON" else "OUTPUT_LVCMOS33"),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "BANK.LVDS", ["OFF", "ON"],
                                         lambda x: get_substs(
                                             iomode="INPUT_LVDS" if x == "ON" else "NONE"),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "BANK.VREF", ["OFF", "ON"],
                                         lambda x: get_substs(
                                             iomode="INPUT_SSTL15_II" if x == "ON" else "INPUT_LVCMOS15"),
                                         empty_bitfile)


if __name__ == "__main__":
    main()
