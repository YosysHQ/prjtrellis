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
    cfg.ncl = "ccu2.ncl"

    def per_slice(slicen):
        def get_substs(ij1_0="YES", ij1_1="YES"):
            return dict(slice=slicen, ij1_0=ij1_0, ij1_1=ij1_1)
        nonrouting.fuzz_enum_setting(cfg, "SLICE{}.CCU2.INJECT1_0".format(slicen), ["YES", "NO"],
                                     lambda x: get_substs(ij1_0=x),
                                     empty_bitfile, True)
        nonrouting.fuzz_enum_setting(cfg, "SLICE{}.CCU2.INJECT1_1".format(slicen), ["YES", "NO"],
                                     lambda x: get_substs(ij1_1=x),
                                     empty_bitfile, True)
    fuzzloops.parallel_foreach(["A", "B", "C", "D"], per_slice)


if __name__ == "__main__":
    main()
