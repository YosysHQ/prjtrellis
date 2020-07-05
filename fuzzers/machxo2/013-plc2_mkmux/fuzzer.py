from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import nets
import pytrellis
import re

# No evidence this affects any bits.

cfg = FuzzConfig(job="PLC2MKMUX", family="MachXO2", device="LCMXO2-1200HC", ncl="empty.ncl", tiles=["R10C11:PLC"])


def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "mkmux.ncl"

    def per_slice(slicen):
        def get_substs(m0mux="M0", m1mux="M1", f_mode="F"):
            if m0mux == "OFF":
                s_m0mux = "#OFF"
            else:
                s_m0mux = m0mux
            return dict(slice=slicen, m0mux=s_m0mux, m1mux=m1mux)
        nonrouting.fuzz_enum_setting(cfg, "SLICE{}.M0MUX".format(slicen), ["M0", "OFF", "0"],
                                     lambda x: get_substs(m0mux=x),
                                     empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "SLICE{}.M1MUX".format(slicen), ["M1", "OFF", "0"],
                                     lambda x: get_substs(m1mux=x),
                                     empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "SLICE{}.F0".format(slicen), ["F", "OFF", "0"],
                                     lambda x: get_substs(f_mode=x),
                                     empty_bitfile, False)
    fuzzloops.parallel_foreach(["A", "B", "C", "D"], per_slice)


if __name__ == "__main__":
    main()
