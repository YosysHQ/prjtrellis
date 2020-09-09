module dcc_test2(input clki, input ce0, input ce1, output clko);

wire clk_int;

// Despite EPIC claiming more DCCs exist, and the synthesizer accepting
// the LOC constraint, trying to use the other DCCs causes an assertion failure
// during placement!

DCCA I1 (.CLKI (clki), .CE (ce0), .CLKO (clk_int));
DCCA I2 (.CLKI (clk_int), .CE (ce1), .CLKO (clko))  /* synthesis LOC=DCC_R6C14_0B */;

endmodule
