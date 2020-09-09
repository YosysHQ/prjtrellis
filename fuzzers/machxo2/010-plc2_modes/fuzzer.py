from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import nets
import pytrellis
import re

cfg = FuzzConfig(job="PLC2MODE", family="MachXO2", device="LCMXO2-1200HC", ncl="empty.ncl", tiles=["R10C11:PLC"])


def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "modes.ncl"

    def per_slice(slicen):
        def get_substs(mode):
            return dict(slice=slicen, mode=mode)
        if slicen == "A" or slicen == "B":
            modes = ["LOGIC", "CCU2", "DPRAM"]
        elif slicen == "C":
            modes = ["LOGIC", "CCU2", "RAMW"]
        else:
            modes = ["LOGIC", "CCU2"]
        nonrouting.fuzz_enum_setting(cfg, "SLICE{}.MODE".format(slicen), modes,
                                     lambda x: get_substs(mode=x),
                                     empty_bitfile, False)

    fuzzloops.parallel_foreach(["A", "B", "C", "D"], per_slice)


if __name__ == "__main__":
    main()
