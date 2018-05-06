#!/usr/bin/env python3
"""
This simple example uses PyTrellis to unpack and pack a bitstream
"""
import pytrellis

pytrellis.load_database("../../../prjtrellis-db")
bs = pytrellis.Bitstream.read_bit("../../minitests/lut/lut.bit")
chip = bs.deserialise_chip()
repack = pytrellis.Bitstream.serialise_chip(chip)
repack.write_bit("repack.bit")
