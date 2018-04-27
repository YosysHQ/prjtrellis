Tiles
=================

The ECP5 FPGA is structured as a grid of tiles. This grid can be visualised
by looking at the HTML output of ``tile_html.py``.

Tiles have a name, for example *MIB_R13C6* and a type, for example **MIB_DSP2**.
The name also encodes a position, in this case row 13, column 6. Multiple tiles may be
located in the same grid square.

Tiles also have an offset in the bitstream in terms of frames and bits within frames, and
a bitstream size in terms of frames and bits within frames.

Logic Tiles
-----------
All logic tiles are of type **PLC2**.

Logic Tiles contain 4 slices and routing fabric. The routing fabric in a logic tile
can connect slices to general and global routing; and connect together general routing
wires.

Each slice contains 2 LUTs, 2 flip-flops and fast carry logic. All slices can also be configured
to function as distributed RAM.

Common Interconnect Blocks (CIBs)
----------------------------------
Common Interconnect Blocks (CIBs) are used to connect special functions - everything other than slices - to the routing fabric.
They are effectively a logic tile with the slices removed, and the signals that would connect to the slice
are connected to inputs and outputs from those special functions. Special functions in this context includes
IO, EBR, DSPs, PLLs, etc. Note that the names of these signals do not reflect the IO of the special function, but are always
named as if they were connected to a slice. Part of Project Trellis will thus be determining this mapping.

There are several types of CIB depending on what they connect to and their location on the chip. For example:

 - **CIB** tiles connect to top and bottom IO, and **CIB_LR** connect to left and right IO.
 - **CIB_EBR** tiles connect to EBR.
 - **CIB_DSP** tiles connect to the hard DSPs.
 - **CIB_PLLx** tiles connect to the PLLs.
 - **CIB_DCUx** tiles connect to the SERDES duals (DCUs).

Most CIBs contain a **CIBTEST** component, which has an unknown function in Lattice testing but is not used for user designs.

IO Tiles
---------
There are several different types of IO tiles depending on the position in the device. In all cases, each
IO pin is represented by two sites: an IO buffer (``PIO``) and IO registers/gearboxes (``IOLOGIC``).

Depending on the location in the device, IO pins are arranged in quads (A-D) or pairs (A-B).

 - IO at the top of the device uses a total of four tiles for each pair of IO. **PIOT0** and **PIOT1** contain ``PIOA`` and ``PIOB``
   split between them, and **PICT0** and **PICT1** contain ``IOLOGICA`` and ``IOLOGICB``.
 - IO at the left and right of the device use a total of three tiles for each quad of IO. Note that in this
   context *x* is **L** for left IO and **R** for right IO. **PICx1** contains all four PIO, **PICx0** contains ``IOLOGICA`` and ``IOLOGICB``,
   and **PICx2** usually contains ``IOLOGICC`` and ``IOLOGICD``. In some cases, ``IOLOGICC`` and ``IOLOGICD`` are placed inside a **MIB_CIB_LR** tile
   instead.
 - IO at the bottom of the device uses a total of two tiles for each pair of IO. **PICB0** and **PICB1** contain both PIO and IOLOGIC split
   between them.

Additionally **BANKREFx** tiles contain per-bank IO configuration for reference voltages and VccIO.

Global Clock Tiles
-------------------
Several different tiles have functions in global clock routing. See :doc:`Global Routing <global_routing>` for more information on exact
connections and blocks involved.

 - **TAP_DRIVE** and **TAP_DRIVE_CIB** tiles, arranged in several columns and present in all rows, selectively connect
   vertical global clocks coming in from the spine for the relevant quadrant to horizontal clock routing
   for the associated row section.
 - **CMUX_xx** tiles form the central global clock muxes for each quadrant, selecting clocks from the **xMID** tiles, feeding the spine tiles.
   In some cases these are split and/or combined with another function (such as DSP or EBR). These also contain the two clock selectors (DCSs).
 - **xMID_x** tiles select various input clocks and feed them to the central clock mux, providing a clock gate (DCC)
   for each clock.
 - **ECLK_L** and **ECLK_R** select the IO edge clocks.
 - **x_SPINE_xx** tiles selectively connect the outputs from the central clock muxes to the vertical wires feeding the **TAP_DRIVE** s. These are combined with another function, EBR or DSP
   and located in EBR/DSP rows.

Embedded Block RAM (EBR)
------------------------

The EBR is distributed such that 9 columns contain 4 EBRs (each EBR is 18kbit). The tiles containing
the EBR sites themselves, and the EBR configuration bits, are named **MIB_EBR0** to **MIB_EBR8**. The
EBR is connected to the routing fabric using **CIB_EBR** tiles in the same row as the **MIB_EBRx** tiles.
The meaning of *MIB* is unknown, it likely comes from Maco Interface Tile (Maco was a hybrid FPGA/ASIC technology
previously used by Lattice).

The EBR configuration is split thus:

+-----+-----------------------------------------------+
| EBR | Tiles                                         |
+=====+===============================================+
| 0   | **MIB_EBR0**, **MIB_EBR1**                    |
+-----+-----------------------------------------------+
| 1   | **MIB_EBR2**, **MIB_EBR3**, **MIB_EBR4**      |
+-----+-----------------------------------------------+
| 2   | **MIB_EBR4**, **MIB_EBR5**, **MIB_EBR6**      |
+-----+-----------------------------------------------+
| 3   | **MIB_EBR6**, **MIB_EBR7**, **MIB_EBR8**      |
+-----+-----------------------------------------------+

EBR initialisation is done using separate commands in the bitstream, not from within the EBR tiles themselves.

DSP Tiles
----------

DSPs are distributed such that 9 columns contain 2 18x18 sysDSP slices. Two tiles per column (on the same row)
contain the DSP sites themselves, and the DSP configuration bits, and are named **MIB_DSP0** to **MIB_DSP8** and
**MIB2_DSP0** to **MIB2_DSP8**. The DSPs are connected to the routing fabric using **CIB_DSP**
tiles in the same row as the **MIBx_DSPx** tiles.

System and Config Tiles
------------------------

There are several tiles, usually only one of each per device, which contain miscellaneous system functions and global
device settings. For example:

 - **EFBx_PICBx** tiles (which are combined with bottom IO tiles) contain config port related settings such as which ports are
   enabled after configuration, whether TransFR is enabled, and the speed of the internal oscillator. They also contain configuration
   related to the global set/reset signal.
 - **DTR** contains the Digital Temperature Readout function.
 - **POR** contains a single bit to disable power-on reset.
 - **OSC** contains the internal oscillator.
 - **PVT_COUNTx** are related to Process/Voltage/Temperature compensation and contain a PVTTEST component for Lattice testing.

