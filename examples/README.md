# Examples of the Yosys + nextpnr + Trellis Flow

These are some simple examples of the Project Trellis flow. Currently only IO and logic (LUTs/FFs) are supported,
with more features to be implemented shortly.

## Disclaimer

Project Trellis is currently **highly** experimental. Do not use it for anything mission critical like avionics, nuclear power or automatic cat feeders!
Although I have not managed to destroy any FPGAs, there is a non-zero chance that the tools could produce a bitstream that destroys or degrades the FPGA. Do not
use with a development board that you cannot afford to lose!

## Prerequisites

You must have [Yosys](https://github.com/YosysHQ/yosys), [nextpnr](https://github.com/YosysHQ/nextpnr) and [Trellis](https://github.com/SymbiFlow/prjtrellis)
installed **from the latest Git master** to use the flow. Refer to the READMEs of each project for more information on building and installing them.

## Included Projects

 - **tinyfpga**: morse blink example for the TinyFPGA Ex rev1 prototype with an 85k ECP5
 - **ulx3s**: "Night Rider" example for the 45k ULX3S board
 - **versa**: 14-segment display example for the ECP5 Versa Board

All projects include a Makefile for building (and programming in the case of the TinyFPGA example).

## Notes

In all cases there are a handful of constant bits (that remain the same in all ECP5 designs), whose detailed function
is unknown - even if the low-level purpose, such as tying an internal signal low, is known. This is why there is a
"_empty.config" file in all examples. These files are also located in the `misc/basecfgs` folder. If you need to
change any of the examples to a different ECP5 device, you will also need to pick the appropriate base config.

IO constraints are currently specified as attributes on `TRELLIS_IO` primitives, reading IO constraint files
is not yet implemented.
