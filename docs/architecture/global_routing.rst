Global Routing
===============

The ECP5's global clock routing is split into a number of parts. A high level overview of its structure is contained
in Lattice Technical Note TN1263.

From a point of view of clock distribution, the device is split into four quadrants: upper left (UL), upper right (UR),
lower left (LL) and lower right (LR). Throughout this document, *qq* refers to any quadrant named in this way,
*s* refers to a side of the device (B, T, L, or R).

This document is a work in progress! Some information is still incomplete and subject to change.

Mid Muxes
----------
The mid muxes are located in the middle of each edge of the device, and take clock inputs from a range of sources
(clock input pins, PLL ouputs, CLKDIV outputs, etc) and feed them into the centre clock muxes.

Depending on the location, mid muxes have between 12 and 16 outputs to the centre muxes.

Between each mid mux multiplexer output and the centre mux is a Dynamic Clock Control component (DCC),
which provides glitch free clock disable.

Inputs to the mid muxes are named as follows:

 - **PCLKx_y** for the dedicated clock input pins
 - **qqC_PCLKGPLLx_y** for the PLL outputs
 - **s_CDIVX_x** for the clock divider outputs
 - **qqQ_PCLKCIB_x** and **qqM_PCLKCIBx** have unknown function, most likely a connection to fabric (TODO: check)
 - **PCSx_TXCLK_y** and **PCSx_RXCLK_y** are the SERDES transmit and receive clocks
 - **SERDES_REFCLK_x** are the SERDES reference clocks

Outputs from the muxes themselves into the DCCs are named **sDCC00CLKI** through **sDCCnnCLKI**.

The outputs from the DCCs into the centre muxes are named **HPFE0000** through **HPFE1300** for the left side;
**HPFW0000** through **HPFW1300** for the right side; **VPFN0000** through **VPFN1500** for the bottom side and
**VPFS0000** through **VPFS1100** for the top side.

The left and right muxes are located in a single tile, **LMID_0** and **RMID_0** respectively. The top side is
split between **TMID_0** and **TMID_1**, and the bottom side between **BMID_0** and **BMID_2V**.

Centre Muxes
------------

The centre muxes select the 16 global clocks for each quadrant from the outputs of the mid muxes and from a few other
sources. They also contain a total of two Dynamic Clock Select blocks, for glitch-free clock switching.

There are four fabric entries to the centre muxes from each of the four quadrants. These connect through DCCs in the
same way as the mid mux outputs (but in this case the DCC is considered as part of the centre mux rather than mid mux).

The fabric entries come from nearby CIBs, but the exact net still need to be traced.

Inputs to the mid muxes (and DCSs) are named as follows:

 - **HPFExx00**, **HPFWxx00**, **VPFNxx00** and **VPFSxx00** for the mid mux (via DCC) outputs
 - **qqCPCLKCIB0** for the fabric clock inputs (via DCC)
 - **DCSx** for the DCS outputs
 - **VCC_INT** for constant one

Outputs from the centre muxes, going into the spine tiles, are named **qqPCLK0** through **qqPCLK15**.

Centre muxes also contain *CLKTEST*, a component with unknown function used in Lattice's testing.

The exact split of centre mux functionality between tiles varies depending on device, this is an example
for the LFE5U-85F.

+-------------+---------------+-----------------------------------------+-----------------+
| Tile        | Tile Type     | Functions                               | Notes           |
+=============+===============+=========================================+=================+
| MIB_R22C66  | EBR_CMUX_UL   | DCS0 config, CLKTEST                    | Shared with EBR |
+-------------+---------------+-----------------------------------------+-----------------+
| MIB_R22C67  | CMUX_UL_0     | UL clocks mux, DCS0CLK0 input mux, DCC2 |                 |
+-------------+---------------+-----------------------------------------+-----------------+
| MIB_R22C68  | CMUX_UR_0     | UR clocks mux, DCS0CLK1 input mux, DCC3 |                 |
+-------------+---------------+-----------------------------------------+-----------------+
| MIB_R22C69  | EBR_CMUX_UR   | CLKTEST                                 | Shared with EBR |
+-------------+---------------+-----------------------------------------+-----------------+
| MIB_R70C66  | EBR_CMUX_LL   | DCS1 config, CLKTEST                    | Shared with EBR |
+-------------+---------------+-----------------------------------------+-----------------+
| MIB_R70C67  | CMUX_LL_0     | LL clocks mux, DCS1CLK0 input mux, DCC0 |                 |
+-------------+---------------+-----------------------------------------+-----------------+
| MIB_R70C68  | CMUX_LR_0     | LR clocks mux, DCS1CLK1 input mux, DCC1 |                 |
+-------------+---------------+-----------------------------------------+-----------------+
| MIB_R70C69  | EBR_CMUX_LR   | CLKTEST                                 | Shared with EBR |
+-------------+---------------+-----------------------------------------+-----------------+

Spine Tiles
------------
The outputs from the centre muxes go horizontally into each quadrant and connect to a few spine tiles (there are three
spine tiles per quadrant in the 85k part). Spine tiles are located adjacent to a column of TAP_DRIVEs (see next section)
and are combined with another function (EBR or DSP).

The purpose of a spine tile is to selectively connect the centre mux outputs to the vertical global wires feeding the
adjacent column of TAP_DRIVEs through a buffer. There is one buffer per wire, with a 1:1 mapping - the only reason
spine tiles are configurable is to disable unused buffers to save power, there is no other routing or selection
capability in them.

The inputs to spine tiles from the quadrant's centre mux are named **qqPCLK0** through **qqPCLK15**.

The outputs are named **VPTX0000** through **VPTX15000**, which feed a column of tap drives.

TAP_DRIVE Tiles
---------------
TAP_DRIVE tiles are arranged in columns throughout the device.

The purpose of TAP_DRIVE tiles is to selectively connect the vertical global wires coming out of the adjacent spine tile
to horizontal wires serving tiles to the left and right of the TAP_DRIVE. A TAP_DRIVE will typically serve a row of
about 20 tiles, 10 to the left and 10 to the right.

Like spine tiles, TAP_DRIVE tiles have a 1:1 input-output mapping and only offer the ability to turn on/of buffers
to save power.

The outputs are named **HPBX0000** through **HPBX15000**, with a net location on the left or right for the left or
right outputs (signified as **L_** or **R_** in the Project Trellis database.

Non-Clock Global Usage
-----------------------
Inside PLBs, global nets can not only be connected to the clock signal, but also to clock enable, set/reset and general
local wires. This does not seem to be commonly used by Diamond, which prefers to use general routing and the GSR signal.

Not all globals can be used for all functions, the allowed usage depending on net is shown below.

+--------+-----+-----+-----+-------+
| Global | CLK | LSR | CEN | Local |
+--------+-----+-----+-----+-------+
| 0      | Y   |     |     | Y     |
+--------+-----+-----+-----+-------+
| 1      | Y   |     |     | Y     |
+--------+-----+-----+-----+-------+
| 2      | Y   |     |     | Y     |
+--------+-----+-----+-----+-------+
| 3      | Y   |     |     | Y     |
+--------+-----+-----+-----+-------+
| 4      | Y   | Y   |     | Y     |
+--------+-----+-----+-----+-------+
| 5      | Y   | Y   |     | Y     |
+--------+-----+-----+-----+-------+
| 6      | Y   | Y   |     | Y     |
+--------+-----+-----+-----+-------+
| 7      | Y   | Y   |     | Y     |
+--------+-----+-----+-----+-------+
| 8      | Y   | Y   |     |       |
+--------+-----+-----+-----+-------+
| 9      | Y   |     | Y   |       |
+--------+-----+-----+-----+-------+
| 10     | Y   |     | Y   |       |
+--------+-----+-----+-----+-------+
| 11     | Y   |     | Y   |       |
+--------+-----+-----+-----+-------+
| 12     | Y   |     | Y   |       |
+--------+-----+-----+-----+-------+
| 13     | Y   |     | Y   |       |
+--------+-----+-----+-----+-------+
| 14     | Y   | Y   | Y   |       |
+--------+-----+-----+-----+-------+
| 15     | Y   | Y   | Y   |       |
+--------+-----+-----+-----+-------+
