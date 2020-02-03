from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import nets
import pytrellis
import re

cfg = FuzzConfig(job="PLC2REG", family="MachXO2", device="LCMXO2-1200HC", ncl="empty.ncl", tiles=["R10C6:PLC"])


def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "lsr.ncl"

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
        nonrouting.fuzz_enum_setting(cfg, "LSR{}.LSRMUX".format(lsrn), ["LSR", "INV"],
                                     lambda x: get_substs(lsrmux=x),
                                     empty_bitfile, True)
        nonrouting.fuzz_enum_setting(cfg, "LSR{}.SRMODE".format(lsrn), ["LSR_OVER_CE", "ASYNC"],
                                     lambda x: get_substs(srmode=x),
                                     empty_bitfile, True)
        nonrouting.fuzz_enum_setting(cfg, "LSR{}.LSRONMUX".format(lsrn), ["0", "LSRMUX"],
                                     lambda x: get_substs(lsronmux=x),
                                     empty_bitfile, True)
    fuzzloops.parallel_foreach(["0", "1", "2", "3"], per_lsr)


if __name__ == "__main__":
    main()
