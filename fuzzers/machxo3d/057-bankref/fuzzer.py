from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import argparse
import dbcopy

jobs = [
    # Bank 0
    {
        "cfg": FuzzConfig(job="PIC_T_DUMMY_VIQ", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty_9400.ncl",
                          tiles=["PT25:PIC_T_DUMMY_VIQ"]),
        "pin": "A3",
        "side": "T",
        "bank": "0"
    },

    # Bank 1
    {
        "cfg": FuzzConfig(job="CIB_EBR2_END1_10K", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty_9400.ncl",
                          tiles=["CIB_R15C49:CIB_EBR2_END1_10K"]),
        "pin": "H14",
        "side": "R",
        "bank": "1"
    },

    # Bank 2
    {
        "cfg": FuzzConfig(job="PIC_B_DUMMY_VIQ_VREF", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty_9400.ncl",
                          tiles=["PB25:PIC_B_DUMMY_VIQ_VREF"]),
        "pin": "R7",
        "side": "B",
        "bank": "2"
    },

    # Bank 4
    {
        "cfg": FuzzConfig(job="PIC_L0_VREF3", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty_9400.ncl",
                          tiles=["PL12:PIC_L0_VREF4"]),
        "pin": "G1",
        "side": "L",
        "bank": "4"
    },
]

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
                                       ignore_bits=([("CIB_R15C49:CIB_EBR2_END1_10K", 13, 9), ("CIB_R15C49:CIB_EBR2_END1_10K", 13, 12)]))
 
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
                                        ignore_bits=([("PB25:PIC_B_DUMMY_VIQ_VREF", 5, 14)]))

        if side in ('T'):
            nonrouting.fuzz_enum_setting(cfg, "BANK.LVDSO", ["OFF", "ON"],
                                            lambda x: get_substs(
                                                iomode="OUTPUT_LVDS25" if x == "ON" else "OUTPUT_LVCMOS25D"),
                                            empty_bitfile)

    for dest in ["CIB_EBR2_END1"]:
        dbcopy.copy_enums_with_predicate("MachXO3D", "LCMXO3D-9400HC", "CIB_EBR2_END1_10K", dest, include_bank_enum)
    for dest in ["LLC0PIC_I3C_VREF3", "LLC1", "PIC_L1_VREF4", "PIC_L0_VREF5", "PIC_L1_VREF5"]:
        dbcopy.copy_enums_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_L0_VREF4", dest, include_bank_enum)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PIO Attributes Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
