# Purpose
This example contains two separate verilog implementations
1) Blinks LED 0 on EVN board
2) Blinks LED 7 on EVN board

It generates a multiboot.bin file as well as a suitable multiboot.mcs file.
Once flashed, pressing PROGRAMN button will switch between the available
bitstreams.

# Usage
In order to use, it must be flashed to the ECP5-EVN board.
This can be done with the official programmer from lattice.
The generated MCS (Intel Hex) file is sufficiently compatible with Lattice to
allow flashing.
However, flashing the bin/hex any other way should also work.
Due to padding with SPI Flash erase byte, it will be significantly faster to
flash the hex file.

