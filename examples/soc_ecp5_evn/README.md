# PicoRV32 example for ECP5-EVN board

This is a port of the soc-versa5g for the ECP5-EVN board.

## Clock

This example uses the 12Mhz FTDI clock as input for the PLL and gives a 50Mhz clock
for the CPU and UART.

This clock is output on Pin A19 for verification purposes

## UART

By default, the UART is not hooked up to the FTDI.
To make the UART work, you need to solder the following zero-ohm resistors:

* R34
* R35
* R21 (Optional for UART Activity LED)

