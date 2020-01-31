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
    cfg.ncl = "clkmux.ncl"

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
        nonrouting.fuzz_enum_setting(cfg, "CLK{}.CLKMUX".format(clkn), ["CLK", "INV", "0", "1"],
                                     lambda x: get_substs(clkmux=x),
                                     empty_bitfile, True)

    fuzzloops.parallel_foreach(["0", "1", "2", "3"], per_clk)


if __name__ == "__main__":
    main()
