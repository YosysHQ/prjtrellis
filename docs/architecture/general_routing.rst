General Routing
===============

The ECP5's general routing is unidirectional and relatively straightforward. They are detailed below. The inputs and
outputs of the routing inside tiles are:

 - The inputs to BELs are named **A0**-**A7**, **B0**-**B7**, **C0**-**C7**, **D0**-**D7** (LUT inputs),
   **M0**-**M7** ("miscellaneous" inputs for muxes and other functions); **LSR0** and **LSR1** (local set/reset);
   **CLK0** and **CLK1** (clock) and **CE0**-**CE3** (clock enable), for logic tiles.

 - The outputs are named **F0** to **F7** (LUT outputs) and **Q0** to **Q7** (FF outputs).

 - CIB tiles have an identical routing configuration to logic tiles, regardless of what they connect to  - effectively,
   the logic slices are replaced by the special function - however, all the netnames aboved are prefixed with **J**.
   Fixed arcs connect the CIB signals to the signals inside the special function tile.

Four types of routing resource are available:

 - 8 ***X0** wires inside each tile (**H00L0x00**, **H00R0x00**, **V00T0x00**, and **V00B0x00**) do not leave a tile,
   but can be driven from a variety of internal and external signals; and all of the horizontal or vertical signals
   are inputs to all of the BEL input muxes.
 - 8 **X1** "neighbour" wires originate, and terminate, in each tile (**H01E0x01**, **H01W0x00**, **V01S0x00** and
   **V01N0x01**). These connect together adjacent tiles in the specified direction, and can be driven by any of the
   LUT or FF outputs as well as a few other signals.
 - 32 **X2** span-2 wires (**H02E0x01**, **H02W0x01**, **V02S0x01** and **V02N0x01**) originate in each tile, each
   connecting to the two next tiles in a given direction.
 - 16 **X6** span-6 wires (**H06E0x03**, **H06W0x03**, **V06S0x03** and **V06N0x03**) originate in each tile
   connecting to two tiles, with a gap of 2 inbetween each, in a given direction.

In all cases, wires can only be driven inside one tile. **X2** and **X6** inputs only drive muxes in tiles other than
the tile they originate in; whereas **X0** and **X1** also "bounce back" internally (this being the very purpose of
**X0** tiles).
