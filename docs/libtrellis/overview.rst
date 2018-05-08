libtrellis Overview
====================

libtrellis is a C++ library containing utilities to manipulate ECP5 bitstreams, and the databases that correspond tile
bits to functionality (routing and configuration). Although libtrellis can be used as a standard shared library, its
primary use in Project Trellis is as a Python module (called pytrellis), imported by the fuzzing and utility scripts.
The C++ classes are bound to Python using Boost::Python.

Bitstream
---------
This class provides functionality to read and write Lattice bitstream files, parse their commands, and convert them
into a chip's configuration memory (in terms of frames and bits).

To read a bitstream, use ``read_bit`` to create a ``Bitstream`` object, then call ``deserialise_chip`` on that to
create a ``Chip``.

Chip
-----
This represents a configured FPGA, in terms of its configuration memory (``CRAM``), tiles and metadata. You can either
use ``deserialise_chip`` on a bitstream to construct a Chip from an existing bitstream, or construct a Chip by device
name or IDCODE.

The ``ChipInfo`` structure contains information for a particular FPGA device.

CRAM
-----
This class stores the entire configuration data of the FPGA, as a 2D array (frames and bits). Although the array can be
accessed directly, many cases will use ``CRAMView`` instead. ``CRAMView`` provides a read/write view of a window of the
CRAM. This is usually used to represent the configuration memory of a single tile, and takes frame and bit offsets
and lengths.

Subtracting two ``CRAMView`` s, if they are the same size, will produce a ``CRAMDelta``, a list of the changes between
the two memories. This is useful for fuzzing or comparing bitstreams.

Tile
-----
This represents a tile of the FPGA. It includes a ``CRAMView`` to represent the configuration memory of the tile.

TileConfig
-----------
This represents the actual configuration of a tile, in terms of arcs (programmable connections), config words (such as
LUT initialisation) and config enums (such as IO type). It is the result of decoding the tile CRAM content using the bit
database, and can be converted to a FASM-like format.

