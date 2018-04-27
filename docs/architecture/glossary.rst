Glossary
========================

.. glossary::

  Arc
    A programmable connection between two nodes. Most arcs are unidirectional buffers that connect
    in one direction only, a few are bidirectional switch transistors (however these are mostly used in
    situations where this is one useful direction anyway).

  ASIC
    An application-specific integrated circuit (ASIC) is a chip that is
    designed and used for a specific purpose, such as video acceleration,
    machine learning acceleration, and many more purposes. In contrast to
    :term:`FPGAs <FPGA>`, the programming of an ASIC is fixed at the time of
    manufacture.

  Bitstream
    Binary data that is directly loaded into an :term:`FPGA` to perform
    configuration. Contains configuration :term:`frames <frame>` as well as
    programming sequences and other commands required to load and activate same.

  Database
    Contains information about programmable configuration bits, arc enable bits,
    and how wires are connected between tiles.

  FF
  Flip flop
    A flip flop (FF) is a logic element on the :term:`FPGA` that stores state.

  FPGA
    A field-programmable gate array (FPGA) is a reprogrammable integrated
    circuit, or chip. Reprogrammable means you can reconfigure the integrated
    circuit for different types of computing. You define the configuration via a
    hardware definition language (:term:`HDL`). The word "field" in
    *field-programmable gate array* means the circuit is programmable
    *in the field*, as opposed to during chip manufacture.

  Frame
    A frame contains a row of bits used to configure the FPGA, and is the basic unit
    that a bitstream is split into. The number of bits per frame, and frames per device
    varies for different ECP5 chips.


  Fuzzer
    Scripts and a makefile to generate one or more :term:`specimens <specimen>`
    and then convert the data from those specimens into a :term:`database`.

  General Routing
    Routing that connects together nearby :term:`tiles <tile>` horizontally or vertically, spanning up
    to about 15 tiles at most. Called "shortwires" in Lattice Diamond, but this also refers
    to internal routing.

  Global Routing
    Routing that connects to all :term:`tiles <tile>` in a quadrant for logic, and all tiles
    on an edge for IO. Normally used for routing clocks, or occasionally other high fanout
    signals. Called "longwires" in Lattice Diamond.

  Half
    Portion of a device defined by a virtual line dividing the two sets of global
    clock buffers present in a device. The two halves are referred to as
    the top and bottom halves.

  HDL
    You use a hardware definition language (HDL) to describe the behavior of an
    electronic circuit. Popular HDLs include Verilog (inspired by C) and VHDL
    (inspired by Ada).

  Internal Routing
    Routing that does not leave a single :term:`tile`.

  LUT
    A lookup table (LUT) is a logic element on the :term:`FPGA`. LUTs function
    as a ROM, apply combinatorial logic, and generate the output value for a
    given set of inputs.

  MUX
    A multiplexer (MUX) is a multi-input, single-output switch controled by
    logic.

  Node
    A routing node on the device. A node is a collection of :term:`wires <wire>`
    spanning one or more :term:`tiles <tile>`.
    Nodes that are local to a tile map 1:1 to a wire. A node that spans multiple
    tiles maps to multiple wires, one in each tile it spans.

  PnR
  Place and route
    Place and route (PnR) is the process of taking logic and placing it into
    hardware logic elements on the :term:`FPGA`, and then routing the signals
    between the placed elements. 

  Routing fabric
    The :term:`wires <wire>` and programmable interconnects (:term:`arcs <arc>`)
    connecting the logic blocks in an :term:`FPGA`.

  Site
    Locations inside a tile that can contain an instance of a primitive.

  Specimen
    A :term:`bitstream` of a (usually auto-generated) design with additional
    files containing information about the placed and routed design.
    These additional files are usually generated using programs included with Diamond
    to create debugging outputs.

  Tile
    Fundamental unit of physical structure containing a single type of
    resource or function. The whole chip is a grid of tiles, however, 
    multiple tiles may exist at one grid location.

  Wire
    Physical wire within a :term:`tile`.

