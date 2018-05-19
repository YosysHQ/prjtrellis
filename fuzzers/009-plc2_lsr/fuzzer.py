from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import nets
import pytrellis
import re

cfg = FuzzConfig(job="PLC2REG", family="ECP5", device="LFE5U-25F", ncl="empty.ncl", tiles=["R19C33:PLC2"])


def main():
    pytrellis.load_database("../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "lsr.ncl"

    def per_lsr(lsrn):
        def get_substs(lsrmux="LSR", srmode="LSR_OVER_CE"):
            if lsrmux == "INV":
                lsrmux = "LSR:::LSR=#INV"
            return dict(l=lsrn, lsrmux=lsrmux, srmode=srmode)
        nonrouting.fuzz_enum_setting(cfg, "LSR{}.LSRMUX".format(lsrn), ["LSR", "INV"],
                                     lambda x: get_substs(lsrmux=x),
                                     empty_bitfile, True)
        nonrouting.fuzz_enum_setting(cfg, "LSR{}.SRMODE".format(lsrn), ["LSR_OVER_CE", "ASYNC"],
                                     lambda x: get_substs(srmode=x),
                                     empty_bitfile, True)
    fuzzloops.parallel_foreach(["0", "1"], per_lsr)


if __name__ == "__main__":
    main()
