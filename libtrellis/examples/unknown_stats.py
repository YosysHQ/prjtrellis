#!/usr/bin/env python3
"""
Count the number of known and unknown bits in a chip's bitstream
"""
import pytrellis
import sys

pytrellis.load_database("../../database")
bs = pytrellis.Bitstream.read_bit(sys.argv[1])
chip = bs.deserialise_chip()
total_unknown = 0
total_known = 0
for tile in chip.get_all_tiles():
    tile.dump_config()
    total_unknown += tile.unknown_bits
    total_known += tile.known_bits

print("Total known bits   : {}".format(total_known))
print("Total unknown bits : {}".format(total_unknown))
total_bits = total_known + total_unknown
print("Total set bits     : {}".format(total_bits))
print("Percentage known   : {:.2f}%".format((total_known / total_bits) * 100.0))
