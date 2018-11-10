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
        "cfg": FuzzConfig(job="PIOR", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R35C90:PICR0", "MIB_R36C90:PICR1", "MIB_R37C90:PICR2"]),
        "side": "R",
        "pins": [("L20", "A"), ("M20", "B"), ("L19", "C"), ("M19", "D")]
    },

]



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
                    substs["extra_attrs"] = '(* {}="{}" *)'.format(extracfg[0], extracfg[1])
                if side == "B":
                    substs["cfg_vio"] = get_cfg_vccio(type)
                return substs

            modes = ["NONE"]

            nonrouting.fuzz_enum_setting(cfg, "PIO{}.TERMINATION_1V8".format(pio), ["OFF", "50", "75", "150"],
                                         lambda x: get_substs(iomode="BIDIR_SSTL18_I", extracfg=("TERMINATION", x)),
                                         empty_bitfile, False)

            nonrouting.fuzz_enum_setting(cfg, "PIO{}.TERMINATION_1V5".format(pio), ["OFF", "50", "75", "150"],
                                         lambda x: get_substs(iomode="BIDIR_SSTL15_I", extracfg=("TERMINATION", x)),
                                         empty_bitfile, False)

            nonrouting.fuzz_enum_setting(cfg, "PIO{}.TERMINATION_1V35".format(pio), ["OFF", "50", "75", "150"],
                                         lambda x: get_substs(iomode="BIDIR_SSTL135_I", extracfg=("TERMINATION", x)),
                                         empty_bitfile, False)

            nonrouting.fuzz_enum_setting(cfg, "PIO{}.DIFFRESISTOR".format(pio), ["OFF", "100"],
                                         lambda x: get_substs(iomode="INPUT_LVDS", extracfg=("DIFFRESISTOR", x)),
                                         empty_bitfile, False)

        fuzzloops.parallel_foreach(pins, per_pin)


if __name__ == "__main__":
    main()
