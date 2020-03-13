module top(input clk, ce, lsr, d, t, output p);
	wire tr, q;
	OFS1P3IX oreg_i (.D(d), .SCLK(clk), .SP(ce), .CD(lsr), .Q(q));
	OFS1P3IX treg_i (.D(t), .SCLK(clk), .SP(ce), .CD(lsr), .Q(tr));

	OBZ ob_i(.I(q), .T(tr), .O(p));
endmodule

