from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import nets
import pytrellis
import re

cfg_plc = FuzzConfig(job="PLC2INIT", family="MachXO", device="LCMXO2280C", ncl="empty.ncl", tiles=["R9C5:PLC"])
cfg_fplc = FuzzConfig(job="PLC2INIT", family="MachXO", device="LCMXO2280C", ncl="empty.ncl", tiles=["R2C2:FPLC"])

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
    cfg_plc.setup()
    empty_bitfile = cfg_plc.build_design(cfg_plc.ncl, {})
    cfg_plc.ncl = "lut.ncl"

    def per_slice(slicen):
        for k in range(2):
            def get_substs(bits):
                return dict(slice=slicen, k=str(k), lut_func=get_lut_function(bits))
            nonrouting.fuzz_word_setting(cfg_plc, "SLICE{}.K{}.INIT".format(slicen, k), 16, get_substs, empty_bitfile)

    fuzzloops.parallel_foreach(["A", "B", "C", "D"], per_slice)
    
    cfg_fplc.setup()
    empty_bitfile = cfg_fplc.build_design(cfg_fplc.ncl, {})
    cfg_fplc.ncl = "lut_fplc.ncl"

    def per_slice_fplc(slicen):
        for k in range(2):
            def get_substs(bits):
                return dict(slice=slicen, k=str(k), lut_func=get_lut_function(bits))
            nonrouting.fuzz_word_setting(cfg_fplc, "FSLICE{}.K{}.INIT".format(slicen, k), 16, get_substs, empty_bitfile)

    fuzzloops.parallel_foreach(["A", "B", "C", "D"], per_slice_fplc)

if __name__ == "__main__":
    main()
