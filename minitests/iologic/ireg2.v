module top(input clk, input d, s, output q);
	IFS1P3JX ireg_i (.D(d), .SCLK(clk), .SP(1'b1), .PD(s), 
.Q(q));
endmodule

