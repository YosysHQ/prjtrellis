#!/usr/bin/env python3

import os
from os import path
import shutil

import diamond
from string import Template
import pytrellis

device = "LFE5U-25F"
sink = "R2C2_A0"
# Drivers found using ispTcl
drivers = [
    "R1C2_V02S0501",
    "R2C2_H02W0501",
    "R2C2_H01E0001",
    "R2C3_H02W0701",
    "R2C3_H02W0501",
    "R2C2_H02W0701",
    "R2C2_H02E0501",
    "R3C2_V02N0501",
    "R1C2_V02S0701",
    "R2C2_F5",
    "R2C2_H00L0000",
    "R2C2_F7",
    "R2C2_H02E0701",
    "R2C2_V02N0701",
    "R2C1_H02E0701",
    "R2C3_H01E0001",
    "R2C2_V02S0501",
    "R3C2_V02N0701",
    "R2C2_V02S0701",
    "R2C2_V01N0101",
    "R2C2_V02N0501",
    "R2C1_H02E0501",
    "R2C2_H00L0100",
    "R2C2_H00R0000"
]


def run_get_bits(mux_driver):
    route = ""
    if mux_driver != "":
        route = "route\n\t\t\t" + mux_driver + "." + sink + ";"
    with open("mux_template.ncl", "r") as inf:
        with open("work/mux.ncl", "w") as ouf:
            ouf.write(Template(inf.read()).substitute(route=route))
    diamond.run(device, "work/mux.ncl")
    bs = pytrellis.Bitstream.read_bit("work/mux.bit")
    chip = bs.deserialise_chip()
    tile = chip.tiles["R2C2:PLC2"]
    return tile.cram


def main():
    pytrellis.load_database("../../../prjtrellis-db")
    shutil.rmtree("work", ignore_errors=True)
    os.mkdir("work")
    baseline = run_get_bits("")
    with open("a0_mux_out.txt", "w") as f:
        for d in drivers:
            bits = run_get_bits(d)
            diff = bits - baseline
            diff_str = ["{}F{}B{}".format("!" if b.delta < 0 else "", b.frame, b.bit) for b in diff]
            print("{0: <18}{1}".format(d, " ".join(diff_str)), file=f)
            f.flush()


if __name__ == "__main__":
    main()