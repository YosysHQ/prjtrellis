module top(input I, TS);

USRMCLK mclk_i (.USRMCLKI(I), .USRMCLKTS(TS))
	/* synthesis syn_noprune=1 */;
endmodule