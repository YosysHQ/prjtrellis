module top(input start, output [7:0] dtr);

DTR dtr_i(
	.STARTPULSE(start),
	.DTROUT7(dtr[7]),
	.DTROUT6(dtr[6]),
	.DTROUT5(dtr[5]),
	.DTROUT4(dtr[4]),
	.DTROUT3(dtr[3]),
	.DTROUT2(dtr[2]),
	.DTROUT1(dtr[1]),
	.DTROUT0(dtr[0])
);

endmodule
