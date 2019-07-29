DSP Support
====================

Verilog configurations for the DSP tiles can be generated in Lattice Daimond using Clarity Designer. Unfortunately, those designs cannot currently be compiled by Yosys without some modification. See `NextPnr Issue 208 <https://github.com/YosysHQ/nextpnr/issues/208>`_.

Structure
---------
A DSP tile contains a two input pre-adder which can feed into one of the inputs of a two input multiplier. 1 DSP tile has two multipliers. 
The outputs of the two multipliers feed into a three input adder. 
Two of the three inputs of the three input adder are from the results of the two multipliers.
One tile has two one three input adder. The DSP tiles come in groups of two and the product of the multipliers can either be routed to either of the adders in the two tile group. (Example Coming Soon).

Multiplier
----------
It is currently possible to synthesize a functional pipelined multiplier with 0 - 4 cycles of latency using the yosys-NextPnr flow.

Adder
-----
It should be possible to synthesize an adder - but no working example has been produced yet within the yosys-NextPnr flow.

Macs
----
Multiply accumalates should be possible to synthesize, but no working examples with pre-adders has yet been produced within the yosy-NextPnr flow.
