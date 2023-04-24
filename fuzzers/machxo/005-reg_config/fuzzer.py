from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import nets
import pytrellis
import re

cfg_plc = FuzzConfig(job="PLC2REG", family="MachXO", device="LCMXO2280C", ncl="empty.ncl", tiles=["R9C5:PLC"])
cfg_fplc = FuzzConfig(job="FPLC2REG", family="MachXO", device="LCMXO2280C", ncl="empty.ncl", tiles=["R2C2:FPLC"])


def main():
    pytrellis.load_database("../../../database")
    cfg_plc.setup()
    empty_bitfile = cfg_plc.build_design(cfg_plc.ncl, {})
    cfg_plc.ncl = "reg.ncl"
    cfg_fplc.setup()
    empty_bitfile_fplc = cfg_fplc.build_design(cfg_fplc.ncl, {})
    cfg_fplc.ncl = "reg_fplc.ncl"

    def per_slice_plc(slicen):
        r = 0

        def get_substs(regset="RESET", sd="0", gsr="DISABLED", regmode="FF", clkmode="CLK"):
            return dict(slice=slicen, r=str(r), regset=regset, sd=sd, gsr=gsr, regmode=regmode, clkmode=clkmode)

        for r in range(2):
            nonrouting.fuzz_enum_setting(cfg_plc, "SLICE{}.REG{}.REGSET".format(slicen, r), ["RESET", "SET"],
                                         lambda x: get_substs(regset=x),
                                         empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg_plc, "SLICE{}.REG{}.SD".format(slicen, r), ["0", "1"],
                                         lambda x: get_substs(sd=x),
                                         empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg_plc, "SLICE{}.GSR".format(slicen), ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(gsr=x),
                                     empty_bitfile)

        nonrouting.fuzz_enum_setting(cfg_plc, "SLICE{}.REGMODE".format(slicen), ["FF", "LATCH"],
                                     lambda x: get_substs(regmode=x, clkmode="CLK:::CLK=#INV" if "LATCH" else "CLK"),
                                     empty_bitfile)

    fuzzloops.parallel_foreach(["A", "B", "C", "D"], per_slice_plc)


    def per_slice_fplc(slicen):
        r = 0

        def get_substs(regset="RESET", sd="0", gsr="DISABLED", regmode="FF", clkmode="CLK"):
            return dict(slice=slicen, r=str(r), regset=regset, sd=sd, gsr=gsr, regmode=regmode, clkmode=clkmode)

        for r in range(2):
            nonrouting.fuzz_enum_setting(cfg_fplc, "FSLICE{}.REG{}.REGSET".format(slicen, r), ["RESET", "SET"],
                                         lambda x: get_substs(regset=x),
                                         empty_bitfile_fplc)
            nonrouting.fuzz_enum_setting(cfg_fplc, "FSLICE{}.REG{}.SD".format(slicen, r), ["0", "1"],
                                         lambda x: get_substs(sd=x),
                                         empty_bitfile_fplc)
        nonrouting.fuzz_enum_setting(cfg_fplc, "FSLICE{}.GSR".format(slicen), ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(gsr=x),
                                     empty_bitfile_fplc)
        nonrouting.fuzz_enum_setting(cfg_fplc, "FSLICE{}.REGMODE".format(slicen), ["FF", "LATCH"],
                                     lambda x: get_substs(regmode=x, clkmode="CLK:::CLK=#INV" if "LATCH" else "CLK"),
                                     empty_bitfile_fplc)

    fuzzloops.parallel_foreach(["A", "B", "C", "D"], per_slice_fplc)

if __name__ == "__main__":
    main()
