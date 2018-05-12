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

The contents of ``TileConfig`` are ``ConfigArc`` for connections, ``ConfigWord`` for non-routing configuration words
(which also includes single config bits), ``ConfigEnum`` for enum configurations with multiple textual values, and
``ConfigUnknown`` for unknown bits not found in the database, which are simply stored as a frame, bit reference.

The contents of a tile's configuration RAM can be converted to and from a ``TileConfig`` by using the ``tile_cram_to_config``
and ``config_to_tile_cram`` methods on the ``TileBitDatabase`` instance for the tile.

TileBitDatabase
----------------
There will always be only one ``TileBitDatabase`` for each tile type, which is enforced by requiring calling the
function ``get_tile_bitdata`` (in ``Database.cpp``) to obtain a ``shared_ptr`` to the ``TileBitDatabase``.

The ``TileBitDatabase`` stored the function of all bits in the tile, in terms of the following constructs:

 - Muxes (``MuxBits``) specify a list of arcs that can drive a given node. Each arc (``ArcData``) contains
   specifies source, sink and the list of bits that enable it as a ``BitGroup``.
 - Config words (``WordSettingBits``) specify non-routing configuration settings that are arranged as one or more bits.
   Each config bit has an associated list of bits that enable it. This would be used both for single-bit settings
   and configuration such as LUT initialisation and PLL dividers.
 - Config enums (``EnumSettingBits``) specify non-routing configuration settings that have a set of possible textual
   values, used for either modes/types (i.e. IO type) or occasionally "special" muxes not part of general routing. These
   are specified as a map between possible values and the bits that enable those values.

``TileBitDatabase`` instances can be modified during runtime, in a thread-safe way, to enable parallel fuzzing. They can
be saved back to disk using the ``save`` method.

They can also be used to convert between tile CRAM data and higher level tile config, as described above.
