from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import nets
import pytrellis
import re

cfg = FuzzConfig(job="PLC2REG", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty.ncl", tiles=["R10C11:PLC"])


def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "reg.ncl"

    def per_slice(slicen):
        r = 0

        def get_substs(regset="RESET", sd="0", gsr="DISABLED", regmode="FF"):
            return dict(slice=slicen, r=str(r), regset=regset, sd=sd, gsr=gsr, regmode=regmode)

        for r in range(2):
            nonrouting.fuzz_enum_setting(cfg, "SLICE{}.REG{}.REGSET".format(slicen, r), ["RESET", "SET"],
                                         lambda x: get_substs(regset=x),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "SLICE{}.REG{}.SD".format(slicen, r), ["0", "1"],
                                         lambda x: get_substs(sd=x),
                                         empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "SLICE{}.GSR".format(slicen), ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(gsr=x),
                                     empty_bitfile)
        # The below will be part of SLICE parameters in yosys models to
        # decouple latches from registers. However, fuzz here b/c it makes
        # sense.
        nonrouting.fuzz_enum_setting(cfg, "SLICE{}.REGMODE".format(slicen), ["FF", "LATCH"],
                                     lambda x: get_substs(regmode=x),
                                     empty_bitfile)

    fuzzloops.parallel_foreach(["A", "B", "C", "D"], per_slice)


if __name__ == "__main__":
    main()
