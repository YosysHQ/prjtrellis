from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import nets
import pytrellis
import re

cfg_plc  = FuzzConfig(job="PLC2REG", family="MachXO", device="LCMXO2280C", ncl="empty.ncl", tiles=["R10C6:PLC"])
cfg_fplc = FuzzConfig(job="PLC2REG", family="MachXO", device="LCMXO2280C", ncl="empty.ncl", tiles=["R2C2:FPLC"])


def main():
    pytrellis.load_database("../../../database")

    cfg_plc.setup()
    empty_bitfile_plc = cfg_plc.build_design(cfg_plc.ncl, {})
    cfg_plc.ncl = "lsr_plc.ncl"

    cfg_fplc.setup()
    empty_bitfile_fplc = cfg_fplc.build_design(cfg_fplc.ncl, {})
    cfg_fplc.ncl = "lsr_fplc.ncl"

    def per_lsr(lsrn):
        slices = { "0" : "A",
                   "1" : "B",
                   "2" : "C",
                   "3" : "D"
                 }

        def get_substs(lsrmux="LSR", srmode="LSR_OVER_CE", lsronmux="0"):
            if lsrmux == "INV":
                lsrmux = "LSR:::LSR=#INV"
            return dict(s=slices[lsrn], l=lsrn, lsrmux=lsrmux, srmode=srmode, lsronmux=lsronmux)
        nonrouting.fuzz_enum_setting(cfg_plc, "LSR{}.LSRMUX".format(lsrn), ["LSR", "INV"],
                                     lambda x: get_substs(lsrmux=x),
                                     empty_bitfile_plc,  include_zeros=False)
        nonrouting.fuzz_enum_setting(cfg_plc, "LSR{}.SRMODE".format(lsrn), ["LSR_OVER_CE", "ASYNC"],
                                     lambda x: get_substs(srmode=x),
                                     empty_bitfile_plc, True)
        nonrouting.fuzz_enum_setting(cfg_plc, "LSR{}.LSRONMUX".format(lsrn), ["0", "LSRMUX"],
                                     lambda x: get_substs(lsronmux=x),
                                     empty_bitfile_plc, True)

        nonrouting.fuzz_enum_setting(cfg_fplc, "LSR{}.LSRMUX".format(lsrn), ["LSR", "INV"],
                                     lambda x: get_substs(lsrmux=x),
                                     empty_bitfile_fplc,  include_zeros=False)
        nonrouting.fuzz_enum_setting(cfg_fplc, "LSR{}.SRMODE".format(lsrn), ["LSR_OVER_CE", "ASYNC"],
                                     lambda x: get_substs(srmode=x),
                                     empty_bitfile_fplc, True)
        nonrouting.fuzz_enum_setting(cfg_fplc, "LSR{}.LSRONMUX".format(lsrn), ["0", "LSRMUX"],
                                     lambda x: get_substs(lsronmux=x),
                                     empty_bitfile_fplc, True)

    fuzzloops.parallel_foreach(["0", "1", "2", "3"], per_lsr)


if __name__ == "__main__":
    main()
