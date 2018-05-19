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
    cfg.ncl = "clkmux.ncl"

    def per_clk(clkn):
        def get_substs(clkmux):
            if clkmux == "INV":
                clkmux = "CLK:::CLK=#INV"
            return dict(c=clkn, clkmux=clkmux)
        nonrouting.fuzz_enum_setting(cfg, "CLK{}.CLKMUX".format(clkn), ["CLK", "INV"],
                                     lambda x: get_substs(clkmux=x),
                                     empty_bitfile, True)

    fuzzloops.parallel_foreach(["0", "1"], per_clk)


if __name__ == "__main__":
    main()
