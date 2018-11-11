from fuzzconfig import FuzzConfig
import nonrouting
import nets
import pytrellis
import re
import fuzzloops

jobs = [

    {
        "cfg": FuzzConfig(job="BANKREF8", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                          tiles=["MIB_R71C3:BANKREF8"]),
        "side": "B",
        "pin": "R1"
    },

]


def main():
    pytrellis.load_database("../../../database")
    for job in jobs:
        cfg = job["cfg"]
        side = job["side"]
        pin = job["pin"]
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "pio.v"

        def get_substs(iomode, vcc, extracfg=None):
            if iomode == "NONE":
                iodir, type = "NONE", ""
            else:
                iodir, type = iomode.split("_", 1)
            substs = {
                "dir": iodir,
                "io_type": type,
                "loc": pin,
                "extra_attrs": "",
                "vcc": vcc
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
                                     lambda x: get_substs(iomode=vcco_opts[x], vcc=x.replace("V", ".") if x != "NONE" else "2.5"),
                                     empty_bitfile)



if __name__ == "__main__":
    main()
