#!/usr/bin/env python3
"""
This simple example uses PyTrellis to read TESTTILE tile bits, of tile R2C2 in a bitstream
"""
import pytrellis

pytrellis.load_database("../../../prjtrellis-db")
bs = pytrellis.Bitstream.read_bit("../../minitests/ncl/lut.bit")
chip = bs.deserialise_chip()
tile = chip.tiles["R2C2:PLC2"]
tile_bits = tile.cram
bit_offset = tile.info.bit_offset
frame_offset = tile.info.frame_offset

for bit in range(tile_bits.bits()):
    for frame in range(tile_bits.frames()):
        if tile_bits.bit(frame, bit):
            print("({}, {})\t({}, {})".format(bit, frame, bit + bit_offset, frame + frame_offset))

