from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import nets
import pytrellis
import re

cfg = FuzzConfig(job="PLC2MKMUX", family="ECP5", device="LFE5U-25F", ncl="empty.ncl", tiles=["R19C33:PLC2"])


def main():
    pytrellis.load_database("../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "mkmux.ncl"

    def per_slice(slicen):
        def get_substs(m0mux="M0", m1mux="M1"):
            return dict(slice=slicen, m0mux=m0mux, m1mux=m1mux)
        nonrouting.fuzz_enum_setting(cfg, "SLICE{}.M0MUX".format(slicen), ["M0", "1"],
                                     lambda x: get_substs(m0mux=x),
                                     empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "SLICE{}.M1MUX".format(slicen), ["M1", "1"],
                                     lambda x: get_substs(m1mux=x),
                                     empty_bitfile, False)
    fuzzloops.parallel_foreach(["A", "B", "C", "D"], per_slice)


if __name__ == "__main__":
    main()
