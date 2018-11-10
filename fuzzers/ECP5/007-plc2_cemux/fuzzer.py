from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import nets
import pytrellis
import re

cfg = FuzzConfig(job="PLC2REG", family="ECP5", device="LFE5U-25F", ncl="empty.ncl", tiles=["R19C33:PLC2"])


def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "cemux.ncl"

    def per_slice(slicen):
        def get_substs(cemux):
            if cemux == "INV":
                cemux = "CE:::CE=#INV"
            if cemux == "0":
                cemux = "1:::1=0"
            return dict(slice=slicen, cemux=cemux)
        nonrouting.fuzz_enum_setting(cfg, "SLICE{}.CEMUX".format(slicen), ["0", "1", "CE", "INV"],
                                     lambda x: get_substs(cemux=x),
                                     empty_bitfile, False)

    fuzzloops.parallel_foreach(["A", "B", "C", "D"], per_slice)


if __name__ == "__main__":
    main()
