Textual Configuration Format
============================

Project Trellis supports a simple text-based configuration format so that place-and-route, design manipulation and
design analysis tools do not have to deal with bitstream specifics, nor link directly to libtrellis.

Overview
---------
The text-based configuration format uses standard ASCII text files. ``#`` denotes a comment that continues until the
end of the line. ``.`` at the start of the line followed by the command type denotes a command. Command options follow
on the line, some commands may then have data on subsequent lines until the next command

Non-Tile Configuration
----------------------

``.device <device name>`` specifies the device type, for example ``.device LFE5U-85F``. This should always be the first
command in a file.

``.comment <comment>`` marks the rest of a line as a comment that is included in the header of the bitstream. The FPGA
ignores these, but they may be required if you wish to use vendor programming or deployment tools with the bitstream.

Tile Configuration
------------------

``.tile <tile name>`` denotes the start of a tile. Note that Project Trellis tile names are the Lattice tile name
followed by the colon and the tile type, for example ``MIB_R22C5:MIB_DSP1``. This is because the Lattice tile names
on their own are not unique.

Inside a tile there can be four entries: arcs, words, enums and unknown bits.

``arc: <sink> <source>`` enables an arc inside the tile, using the same Trellis relative netnames as used in the
database, for example ``arc: S3_V06S0303 E1_H01W0100``.

``word: <name> <value>`` sets the value of a configuration word (i.e. a configuration value that can reasonable be
split into bits, such as LUT initialisation). The value is always in binary, MSB first. For example
``word: SLICEC.K0.INIT 0101010101010101`` configures LUT0 in SLICEC to be an inverter.

``enum: <name> <value>`` sets the value of a configuration enum (i.e. a configuration value with multiple textual
values). In all cases one of the values from the Trellis database must be used. For example
``enum: PIOA.BASE_TYPE INPUT_LVCMOS25`` configures PIOA as a LVCMOS25 input.

``unknown: F<frame>B<bit>`` sets an unknown bit, specified by tile-relative frame and bit. For example
``unknown: F95B0`` sets unknown bit 0 in frame 95 in the tile.

Words and enums will not be included when converting a bitstream to textual configuration if they are at their default
value (i.e. the value they would have in a bitstream generated from an empty design).

Beware that some configuration words and enums are split across multiple tiles in features such as IO, EBR and DSPs.
To generate correct bitstreams, they must be included in every tile where they appear. Currently the value matcher, when
converting bitstreams to config looks at each tile individually, so may pick a config that is correct in each tile but
not overall. This will be fixed in the future.

Conversion
-----------

You can use ``libtrellis/examples/bit_to_config.py <bitstream>`` to convert a bitstream to a text config file, and
``libtrellis/examples/config_to_bit.py <config> <bitstream>`` to convert from config to a bitstream. C++ command line
tools and an install script are currently being developed.
