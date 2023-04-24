from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import pytrellis

cfg_plc  = FuzzConfig(job="PLC2REG", family="MachXO", device="LCMXO2280C", ncl="empty.ncl", tiles=["R9C5:PLC"])
cfg_fplc = FuzzConfig(job="PLC2REG", family="MachXO", device="LCMXO2280C", ncl="empty.ncl", tiles=["R5C16:FPLC"])


def main():
    pytrellis.load_database("../../../database")

    cfg_plc.setup()
    empty_bitfile_plc = cfg_plc.build_design(cfg_plc.ncl, {})
    cfg_plc.ncl = "clkmux_plc.ncl"

    cfg_fplc.setup()
    empty_bitfile_fplc = cfg_fplc.build_design(cfg_fplc.ncl, {})
    cfg_fplc.ncl = "clkmux_fplc.ncl"

    def per_clk(clkn):
        slices = { "0" : "A",
                   "1" : "B",
                   "2" : "C",
                   "3" : "D"
                 }

        def get_substs(clkmux):
            if clkmux == "INV":
                clkmux = "CLK:::CLK=#INV"
            if clkmux == "1":
                clkmux = "0:::0=1"
            return dict(c=slices[clkn], clkmux=clkmux)
        nonrouting.fuzz_enum_setting(cfg_fplc, "CLK{}.CLKMUX".format(clkn), ["CLK", "INV", "0", "1"],
                                     lambda x: get_substs(clkmux=x),
                                     empty_bitfile_fplc, True)
        nonrouting.fuzz_enum_setting(cfg_plc, "CLK{}.CLKMUX".format(clkn), ["CLK", "INV", "0", "1"],
                                     lambda x: get_substs(clkmux=x),
                                     empty_bitfile_plc, True)

    fuzzloops.parallel_foreach(["0", "1", "2", "3"], per_clk)


if __name__ == "__main__":
    main()
