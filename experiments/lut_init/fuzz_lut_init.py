#!/usr/bin/env python3

import os
from os import path
import shutil

import diamond
from string import Template
import pytrellis

device = "LFE5U-25F"
lut_inputs = ("A", "B", "C", "D")


def run_get_bits(init_bits):
    sop_terms = []
    for i in range(16):
        if init_bits & (1 << i) != 0:
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
    with open("lut_init_template.ncl", "r") as inf:
        with open("work/lut_init.ncl", "w") as ouf:
            ouf.write(Template(inf.read()).substitute(lut_func=lut_func))
    diamond.run(device, "work/lut_init.ncl")
    bs = pytrellis.Bitstream.read_bit("work/lut_init.bit")
    chip = bs.deserialise_chip()
    tile = chip.tiles["R2C2"]
    return tile.cram


def main():
    pytrellis.load_database("../../../prjtrellis-db")
    shutil.rmtree("work", ignore_errors=True)
    os.mkdir("work")
    baseline = run_get_bits(0)
    with open("lut_bits_out.txt", "w") as f:
        for i in range(16):
            bits = run_get_bits(1 << i)
            diff = bits - baseline
            assert len(diff) == 1
            inv = "!" if diff[0].delta < 0 else ""
            print("INIT[{}]\t{}({}, {})".format(i, inv, diff[0].bit, diff[0].frame), file=f)
            f.flush()


if __name__ == "__main__":
    main()