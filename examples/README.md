# Examples of the Yosys + nextpnr + Trellis Flow

These are some simple examples of the Project Trellis flow. Currently only IO and logic (LUTs/FFs) are supported,
with more features to be implemented shortly.

## Disclaimer

Project Trellis is currently experimental. Do not use it for anything mission critical like avionics, nuclear power or automatic cat feeders!
Although I have not managed to destroy any FPGAs, there is a non-zero chance that the tools could produce a bitstream that destroys or degrades the FPGA. Do not
use with a development board that you cannot afford to lose!

## Prerequisites

You must have [Yosys](https://github.com/YosysHQ/yosys), [nextpnr](https://github.com/YosysHQ/nextpnr) and [Trellis](https://github.com/SymbiFlow/prjtrellis)
installed **from the latest Git master** to use the flow. Refer to the READMEs of each project for more information on building and installing them.

## Included Projects

 - **tinyfpga_rev1/rev2**: morse blink example for the TinyFPGA Ex rev1/2 prototypes with an 85k ECP5
 - **ulx3s**: "Night Rider" example for the 45k ULX3S board
 - **picorv32_ulx3s**: Small picorv32-based SoC for the 45k ULX3S board that displays prime numbers
 on the LEDs.
 - **versa5g**: 14-segment display example for the ECP5 Versa-5G board
 - **picorv32_versa5g**: Small picorv32-based SoC for the ECP5 Versa-5G board that displays prime numbers
 on the LEDs.
 - **soc_versa5g**: Small picorv32-based SoC with RAM and UART for the ECP5 Versa-5G board
 - **ecp5_evn**: "Night Rider" example for the ECP5 Evaluation Board
 - **ecp5_evn_multiboot**: multiboot example for the ECP5 Evaluation Board
 - **soc_ecp5_evn**: Small picorv32-based SoC with RAM and UART for the ECP5 Evaluation Board

All projects include a Makefile for building and programming.


