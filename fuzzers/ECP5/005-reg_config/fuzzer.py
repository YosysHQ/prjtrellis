from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import nets
import pytrellis
import re

cfg = FuzzConfig(job="PLC2REG", family="ECP5", device="LFE5U-25F", ncl="empty.ncl", tiles=["R19C33:PLC2"])


def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "reg.ncl"

    def per_slice(slicen):
        r = 0

        def get_substs(regset="RESET", sd="0", lsrmode="LSR", gsr="DISABLED"):
            return dict(slice=slicen, r=str(r), regset=regset, sd=sd, lsrmode=lsrmode, gsr=gsr)

        for r in range(2):
            nonrouting.fuzz_enum_setting(cfg, "SLICE{}.REG{}.REGSET".format(slicen, r), ["RESET", "SET"],
                                         lambda x: get_substs(regset=x),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "SLICE{}.REG{}.SD".format(slicen, r), ["0", "1"],
                                         lambda x: get_substs(sd=x),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "SLICE{}.REG{}.LSRMODE".format(slicen, r), ["LSR", "PRLD"],
                                         lambda x: get_substs(lsrmode=x),
                                         empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "SLICE{}.GSR".format(slicen), ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(gsr=x),
                                     empty_bitfile)

    fuzzloops.parallel_foreach(["A", "B", "C", "D"], per_slice)


if __name__ == "__main__":
    main()
