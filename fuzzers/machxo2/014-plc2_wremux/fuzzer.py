from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import nets
import pytrellis
import re

cfg = FuzzConfig(job="PLC2WRE", family="MachXO2", device="LCMXO2-1200HC", ncl="empty.ncl", tiles=["R10C11:PLC"])


def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "wremux.ncl"

    def per_slice(slicen):
        def get_substs(wremux):
            if wremux == "INV":
                wremux = "WRE:::WRE=#INV"
            if wremux == "1":
                wremux = "0:::0=1"
            return dict(slice=slicen, wremux=wremux)
        nonrouting.fuzz_enum_setting(cfg, "SLICE{}.WREMUX".format(slicen), ["0", "1", "WRE", "INV"],
                                     lambda x: get_substs(wremux=x),
                                     empty_bitfile, False)

    # B also has a WREMUX signal, but the same bit as A controls it.
    fuzzloops.parallel_foreach(["A"], per_slice)


if __name__ == "__main__":
    main()
