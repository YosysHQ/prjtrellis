from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import nets
import pytrellis
import re

cfg = FuzzConfig(job="PLCINIT", family="MachXO2", device="LCMXO2-4000HC", ncl="empty.ncl", tiles=["R9C9:PLC"])


def get_lut_function(init_bits):
    sop_terms = []
    lut_inputs = ["A", "B", "C", "D"]
    for i in range(16):
        if init_bits[i]:
            p_terms = []
            for j in range(4):
                if i & (1 << j) != 0:
                    p_terms.append(lut_inputs[j])
                else:
                    p_terms.append("~" + lut_inputs[j])
            sop_terms.append("({})".format("*".join(p_terms)))
    if len(sop_terms) == 0:
        lut_func = "0"
    else:
        lut_func = "+".join(sop_terms)
    return lut_func


def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "lut.ncl"

    def per_slice(slicen):
        for k in range(2):
            def get_substs(bits):
                return dict(slice=slicen, k=str(k), lut_func=get_lut_function(bits))
            nonrouting.fuzz_word_setting(cfg, "SLICE{}.K{}.INIT".format(slicen, k), 16, get_substs, empty_bitfile)

    fuzzloops.parallel_foreach(["A", "B", "C", "D"], per_slice)


if __name__ == "__main__":
    main()
