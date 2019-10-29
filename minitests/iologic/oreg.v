module top(input clk, ce, lsr, d, output q);
	OFS1P3IX oreg_i (.D(d), .SCLK(clk), .SP(ce), .CD(lsr), 
.Q(q));
endmodule

