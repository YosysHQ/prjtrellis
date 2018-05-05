#!/usr/bin/env python3
"""
This simple example used PyTrellis to compare logic tile bits, of tile R2C2 in a bitstream
"""
import pytrellis

pytrellis.load_database("../../../prjtrellis-db")
chip_and = pytrellis.Bitstream.read_bit("../../minitests/ncl/lut.bit").deserialise_chip()
chip_or = pytrellis.Bitstream.read_bit("../../minitests/ncl/lut_or.bit").deserialise_chip()

tile_and = chip_and.tiles["R2C2"]
tile_or = chip_or.tiles["R2C2"]
delta = tile_or.cram - tile_and.cram
bit_offset = tile_and.info.bit_offset
frame_offset = tile_or.info.frame_offset

for dbit in delta:
    change = "-" if dbit.delta < 0 else "+"
    bit = dbit.bit
    frame = dbit.frame
    print("{}\t({}, {})\t({}, {})".format(change, bit, frame, bit + bit_offset, frame + frame_offset))

