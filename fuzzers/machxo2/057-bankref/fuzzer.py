from fuzzconfig import FuzzConfig
import nonrouting
import nets
import pytrellis
import re
import fuzzloops
import argparse
import dbcopy
import os

jobs = [
    # Bank 0
    {
        "cfg": FuzzConfig(job="PIC_T_DUMMY_VIQ", family="MachXO2", device="LCMXO2-1200HC", ncl="empty_1200.ncl",
                          tiles=["PT13:PIC_T_DUMMY_VIQ"]),
        "pin": "133",
        "side": "T",
        "bank": "0"
    },

    # Bank 1
    {
        "cfg": FuzzConfig(job="CIB_EBR2_END0", family="MachXO2", device="LCMXO2-1200HC", ncl="empty_1200.ncl",
                          tiles=["CIB_R6C22:CIB_EBR2_END0"]),
        "pin": "98",
        "side": "R",
        "bank": "1"
    },
    # Bank 2
    {
        "cfg": FuzzConfig(job="PIC_B_DUMMY_VREF", family="MachXO2", device="LCMXO2-1200HC", ncl="empty_1200.ncl",
                          tiles=["PB10:PIC_B_DUMMY_VREF"]),
        "pin": "61",
        "side": "B",
        "bank": "2"
    },

    # Bank 3
    {
        "cfg": FuzzConfig(job="PIC_L0_VREF3", family="MachXO2", device="LCMXO2-1200HC", ncl="empty_1200.ncl",
                          tiles=["PL4:PIC_L0_VREF3"]),
        "pin": "23",
        "side": "L",
        "bank": "3"
    },
]#

def include_bank_enum(conn):
    if isinstance(conn, pytrellis.EnumSettingBits):
        name = conn.name
    else:
        name = ""
    if name.startswith("BANK."):
        return True
    return False

def main(args):
    pytrellis.load_database("../../../database")
    for job in [jobs[i] for i in args.ids]:
        cfg = job["cfg"]
        pin = job["pin"]
        side = job["side"]
        os.environ['DEV_PACKAGE'] = "TQFP144"
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "pio.v"

        def get_substs(iomode, extracfg=None, bank=None ):
            if iomode == "NONE":
                iodir, type = "NONE", ""
            else:
                iodir, type = iomode.split("_", 1)
            substs = {
                "dir": iodir,
                "io_type": type,
                "loc": pin,
                "extra_attrs": "",
                "bank": "",
            }
            if extracfg is not None:
                substs["extra_attrs"] = '(* {}="{}" *)'.format(extracfg[0], extracfg[1])
            if bank is not None:
                substs["bank"] = bank
            else:
                substs["bank"] = 1 if job["bank"]=="0" else 0
            return substs

        vcco_opts = {
            "1.2": "OUTPUT_LVCMOS12",
            "1.5": "OUTPUT_LVCMOS15",
            "1.8": "OUTPUT_LVCMOS18",
            "2.5": "OUTPUT_LVCMOS25",
            "3.3": "OUTPUT_LVCMOS33",
            "NONE": "INPUT_LVCMOS33",
        }

        nonrouting.fuzz_enum_setting(cfg, "BANK.INRD", ["OFF", "ON"],
                                  lambda x: get_substs(
                                       iomode="INPUT_LVCMOS33D", bank=job["bank"] if x=="ON" else (1 if job["bank"]=="0" else 0)),
                                       empty_bitfile,
                                       ignore_bits=([("CIB_R6C22:CIB_EBR2_END0", 13, 9), ("CIB_R6C22:CIB_EBR2_END0", 13, 12)]))
 
        nonrouting.fuzz_enum_setting(cfg, "BANK.VCCIO", list(sorted(vcco_opts.keys())),
                                     lambda x: get_substs(iomode=vcco_opts[x]),
                                     empty_bitfile)

        nonrouting.fuzz_enum_setting(cfg, "BANK.DIFF_REF", ["OFF", "ON"],
                                        lambda x: get_substs(
                                            iomode="INPUT_LVCMOS33D" if x == "ON" else "INPUT_LVCMOS33"),
                                        empty_bitfile)
 
        nonrouting.fuzz_enum_setting(cfg, "BANK.VREF", ["OFF", "ON"],
                                        lambda x: get_substs(
                                            iomode="INPUT_LVCMOS25R33" if x == "ON" else "INPUT_LVPECL33"),                                            
                                        empty_bitfile,
                                        ignore_bits=([("PB10:PIC_B_DUMMY_VREF", 5, 14)]))

        if side in ('T'):
            nonrouting.fuzz_enum_setting(cfg, "BANK.LVDSO", ["OFF", "ON"],
                                            lambda x: get_substs(
                                                iomode="OUTPUT_LVDS25" if x == "ON" else "OUTPUT_LVCMOS25D"),
                                            empty_bitfile)

    for dest in ["PIC_B_DUMMY_VIQ_VREF"]:
        dbcopy.copy_enums_with_predicate("MachXO2", "LCMXO2-1200HC", "PIC_B_DUMMY_VREF", dest, include_bank_enum)
    for dest in ["CIB_EBR2_END1"]:
        dbcopy.copy_enums_with_predicate("MachXO2", "LCMXO2-1200HC", "CIB_EBR2_END0", dest, include_bank_enum)
    for dest in ["LLC1", "LLC2", "LLC3PIC_VREF3", "PIC_L1_VREF4", 
                 "PIC_L2_VREF4", "PIC_L3_VREF4", "PIC_L1_VREF5", "PIC_L2_VREF5", "PIC_L3_VREF5"]:
        dbcopy.copy_enums_with_predicate("MachXO2", "LCMXO2-1200HC", "PIC_L0_VREF3", dest, include_bank_enum)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PIO Attributes Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
