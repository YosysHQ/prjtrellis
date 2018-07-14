module top(input clk, input d, output q);
	IFS1P3IX ireg_i (.D(d), .SCLK(clk), .SP(1'b1), .CD(1'b0), 
.Q(q));
endmodule

