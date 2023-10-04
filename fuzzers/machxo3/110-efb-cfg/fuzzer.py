from collections import defaultdict
from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import interconnect

job = (FuzzConfig(job="EFB", family="MachXO3", device="LCMXO3LF-1300E", ncl="empty.ncl",
                  tiles=["CIB_R1C5:CIB_CFG1", "CIB_R1C6:CIB_CFG2", "CIB_R1C7:CIB_CFG3"]))

def get_substs(wbrsti="",wbclki="",i2c2scli="", spiscsn="", tcclki=""):
    comment =""
    efb = ""
    if wbrsti == "INV":
        efb += "WBRSTI=#INV,"
    elif wbrsti == "0":
        efb += "WBRSTI=0,"
    elif wbrsti == "1":
        efb += "WBRSTI=1,"
    else:
        efb += ""
    if wbclki == "INV":
        efb += "WBCLKI=#INV,"
    elif wbclki == "0":
        efb += "WBCLKI=0,"
    elif wbclki == "1":
        efb += "WBCLKI=1,"
    else:
        efb += ""
    if i2c2scli == "INV":
        efb += "I2C2SCLI=#INV,"
    elif i2c2scli == "0":
        efb += "I2C2SCLI=0,"
    elif i2c2scli == "1":
        efb += "I2C2SCLI=1,"
    else:
        efb += ""
    if spiscsn == "INV":
        efb += "SPISCSN=#INV,"
    elif spiscsn == "0":
        efb += "SPISCSN=0,"
    elif spiscsn == "1":
        efb += "SPISCSN=1,"
    else:
        efb += ""
    if tcclki == "INV":
        efb += "TCCLKI=#INV,"
    elif tcclki == "0":
        efb += "TCCLKI=0,"
    elif tcclki == "1":
        efb += "TCCLKI=1,"
    else:
        efb += ""
    return dict(comment=comment, efb=efb)


def main():
    pytrellis.load_database("../../../database")
    cfg = job 
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "efb.ncl"

    nonrouting.fuzz_enum_setting(cfg, "EFB.WBRSTI", ["WBRSTI", "0", "1", "INV"],
                                 lambda x: get_substs(wbrsti=x), empty_bitfile, False)

    nonrouting.fuzz_enum_setting(cfg, "EFB.WBCLKI", ["WBCLKI", "0", "1", "INV"],
                                 lambda x: get_substs(wbclki=x), empty_bitfile, False)

    nonrouting.fuzz_enum_setting(cfg, "EFB.I2C2SCLI", ["I2C2SCLI", "0", "1", "INV"],
                                 lambda x: get_substs(i2c2scli=x), empty_bitfile, False)

    nonrouting.fuzz_enum_setting(cfg, "EFB.SPISCSN", ["SPISCSN", "0", "1", "INV"],
                                 lambda x: get_substs(spiscsn=x), empty_bitfile, False)

    nonrouting.fuzz_enum_setting(cfg, "EFB.TCCLKI", ["TCCLKI", "0", "1", "INV"],
                                 lambda x: get_substs(tcclki=x), empty_bitfile, False)

if __name__ == "__main__":
    main()
