#!/usr/bin/env python3
"""
This simple example uses PyTrellis to unpack and pack a bitstream
"""
import pytrellis, sys

pytrellis.load_database("../../../prjtrellis-db")
bs = pytrellis.Bitstream.read_bit(sys.argv[1])
chip = bs.deserialise_chip()
chip.info.idcode = 0x81112043
tile = chip.tiles["R32C2:PLC2"]
tile_bits = tile.cram
for frame in range(11, 26):
    tile_bits.set_bit(frame, 10, 0)
repack = pytrellis.Bitstream.serialise_chip(chip)
repack.write_bit(sys.argv[2])
