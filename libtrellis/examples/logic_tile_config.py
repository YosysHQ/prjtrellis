#!/usr/bin/env python3
"""
This simple example uses PyTrellis to read TESTTILE tile bits, of tile R2C2 in a bitstream
"""
import pytrellis
import sys

pytrellis.load_database("../../database")
bs = pytrellis.Bitstream.read_bit(sys.argv[1])
chip = bs.deserialise_chip()
for tile in chip.get_tiles_by_type("PLC2"):
    cfg = tile.dump_config()
    if len(cfg.strip()) > 0:
        print(".tile {}".format(tile.info.name))
        print(cfg)
        print()
