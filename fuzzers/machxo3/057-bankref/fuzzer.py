from fuzzconfig import FuzzConfig
import nonrouting
import nets
import pytrellis
import re
import fuzzloops
import argparse
import dbcopy

jobs = [
    # Bank 0
    {
        "cfg": FuzzConfig(job="PIC_T_DUMMY_VIQ", family="MachXO3", device="LCMXO3LF-1300E", ncl="empty_1300.ncl",
                          tiles=["PT13:PIC_T_DUMMY_VIQ"]),
        "pin": "A7",
        "side": "T",
        "bank": "0"
    },

    # Bank 1
    {
        "cfg": FuzzConfig(job="CIB_EBR2_END0", family="MachXO3", device="LCMXO3LF-1300E", ncl="empty_1300.ncl",
                          tiles=["CIB_R6C22:CIB_EBR2_END0"]),
        "pin": "C2",
        "side": "R",
        "bank": "1"
    },
    #{
    #    "cfg": FuzzConfig(job="CIB_EBR2_END1", family="MachXO3", device="LCMXO3LF-2100C", ncl="empty_2100.ncl",
    #                      tiles=["CIB_R8C26:CIB_EBR2_END1"]),
    #    "pin": "D14",
    #    "side": "R"
    #},
    #{
    #    "cfg": FuzzConfig(job="CIB_EBR2_END1_10K", family="MachXO3", device="LCMXO3LF-9400C", ncl="empty_9400.ncl",
    #                      tiles=["CIB_R15C49:CIB_EBR2_END1_10K"]),
    #    "pin": "E22",
    #    "side": "R"
    #},
    # Bank 2
    {
        "cfg": FuzzConfig(job="PIC_B_DUMMY_VREF", family="MachXO3", device="LCMXO3LF-1300E", ncl="empty_1300.ncl",
                          tiles=["PB10:PIC_B_DUMMY_VREF"]),
        "pin": "H9",
        "side": "B",
        "bank": "2"
    },
    #{
    #    "cfg": FuzzConfig(job="PIC_B_DUMMY_VIQ_VREF", family="MachXO3", device="LCMXO3LF-2100C", ncl="empty_2100.ncl",
    #                      tiles=["PB14:PIC_B_DUMMY_VIQ_VREF"]),
    #    "pin": "T5",
    #    "side": "B"
    #},

    # Bank 3
    {
        "cfg": FuzzConfig(job="PIC_L0_VREF3", family="MachXO3", device="LCMXO3LF-1300E", ncl="empty_1300.ncl",
                          tiles=["PL4:PIC_L0_VREF3"]),
        "pin": "D9",
        "side": "L",
        "bank": "3"
    },
    #{
    #    "cfg": FuzzConfig(job="LLC0PIC_VREF3", family="MachXO3", device="LCMXO3LF-9400C", ncl="empty_9400.ncl",
    #                      tiles=["PL30:LLC0PIC_VREF3"]),
    #    "pin": "P4",
    #    "side": "L"
    #},
    #{
    #    "cfg": FuzzConfig(job="LLC1", family="MachXO3", device="LCMXO3LF-4300C", ncl="empty_4300.ncl",
    #                      tiles=["PL21:LLC1"]),
    #    "pin": "M3",
    #    "side": "L"
    #},
    #{
    #    "cfg": FuzzConfig(job="LLC2", family="MachXO3", device="LCMXO3LF-6900C", ncl="empty_6900.ncl",
    #                      tiles=["PL26:LLC2"]),
    #    "pin": "N3",
    #    "side": "L"
    #},
    #{
    #    "cfg": FuzzConfig(job="LLC3PIC_VREF3", family="MachXO3", device="LCMXO3LF-2100C", ncl="empty_2100.ncl",
    #                      tiles=["PL14:LLC3PIC_VREF3"]),
    #    "pin": "L1",
    #    "side": "L"
    #},
    ## Bank 4
    #{
    #    "cfg": FuzzConfig(job="PIC_L0_VREF4", family="MachXO3", device="LCMXO3LF-9400C", ncl="empty_9400.ncl",
    #                      tiles=["PL12:PIC_L0_VREF4"]),
    #    "pin": "L7",
    #    "side": "L"
    #},
    #{
    #    "cfg": FuzzConfig(job="PIC_L1_VREF4", family="MachXO3", device="LCMXO3LF-4300C", ncl="empty_4300.ncl",
    #                      tiles=["PL8:PIC_L1_VREF4"]),
    #    "pin": "J2",
    #    "side": "L"
    #},
    #{
    #    "cfg": FuzzConfig(job="PIC_L2_VREF4", family="MachXO3", device="LCMXO3LF-6900C", ncl="empty_6900.ncl",
    #                      tiles=["PL12:PIC_L2_VREF4"]),
    #    "pin": "J2",
    #    "side": "L"
    #},
    ## Bank 5
    #{
    #    "cfg": FuzzConfig(job="PIC_L0_VREF5", family="MachXO3", device="LCMXO3LF-9400C", ncl="empty_9400.ncl",
    #                      tiles=["PL2:PIC_L0_VREF5"]),
    #    "pin": "D1",
    #    "side": "L"
    #},
    #{
    #    "cfg": FuzzConfig(job="PIC_L1_VREF5", family="MachXO3", device="LCMXO3LF-4300C", ncl="empty_4300.ncl",
    #                      tiles=["PL2:PIC_L1_VREF5"]),
    #    "pin": "E2",
    #    "side": "L"
    #},
    #{
    #    "cfg": FuzzConfig(job="PIC_L2_VREF5", family="MachXO3", device="LCMXO3LF-6900C", ncl="empty_6900.ncl",
    #                      tiles=["PL2:PIC_L2_VREF5"]),
    #    "pin": "F4",
    #    "side": "L"
    #},
    #{
    #    "cfg": FuzzConfig(job="PIC_L3_VREF5", family="MachXO3", device="LCMXO3LF-2100C", ncl="empty_2100.ncl",
    #                      tiles=["PL2:PIC_L3_VREF5"]),
    #    "pin": "E1",
    #    "side": "L"
    #},
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
                substs["bank"] = job["bank"]
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
                                            iomode="INPUT_LVCMOS33D" if x == "ON" else "INPUT_LVCMOS33",
                                            bank=1 if job["bank"]=="0" else 0),
                                        empty_bitfile)
 
        nonrouting.fuzz_enum_setting(cfg, "BANK.VREF", ["OFF", "ON"],
                                        lambda x: get_substs(
                                            iomode="INPUT_LVCMOS25R33" if x == "ON" else "INPUT_LVPECL33",
                                            bank=1 if job["bank"]=="0" else 0),                                            
                                        empty_bitfile,
                                        ignore_bits=([("PB10:PIC_B_DUMMY_VREF", 5, 14)]))

        if side in ('T'):
            nonrouting.fuzz_enum_setting(cfg, "BANK.LVDSO", ["OFF", "ON"],
                                            lambda x: get_substs(
                                                iomode="OUTPUT_LVDS25" if x == "ON" else "OUTPUT_LVCMOS25D"),
                                            empty_bitfile)

    for dest in ["PIC_B_DUMMY_VIQ_VREF"]:
        dbcopy.copy_enums_with_predicate("MachXO3", "LCMXO3LF-1300E", "PIC_B_DUMMY_VREF", dest, include_bank_enum)
    for dest in ["CIB_EBR2_END1", "CIB_EBR2_END1_10K"]:
        dbcopy.copy_enums_with_predicate("MachXO3", "LCMXO3LF-1300E", "CIB_EBR2_END0", dest, include_bank_enum)
    for dest in ["LLC0PIC_VREF3", "LLC1", "LLC2", "LLC3PIC_VREF3", "PIC_L0_VREF4", "PIC_L1_VREF4", 
                 "PIC_L2_VREF4", "PIC_L0_VREF5", "PIC_L1_VREF5", "PIC_L2_VREF5", "PIC_L3_VREF5"]:
        dbcopy.copy_enums_with_predicate("MachXO3", "LCMXO3LF-1300E", "PIC_L0_VREF3", dest, include_bank_enum)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PIO Attributes Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
