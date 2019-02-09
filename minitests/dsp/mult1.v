module dut(
	input clock, reset,
	input din_valid,
	input [31:0] din,
	input dout_ready,
	output dout_valid,
	output [31:0] dout
);
	(* LOC="MULT18_R46C52" *)
	MULT18X18D dsp(
		.A17(1'b0), .A16(1'b0),
		.A15(din[15]), .A14(din[14]), .A13(din[13]), .A12(din[12]), .A11(din[11]), .A10(din[10]), .A9(din[9]), .A8(din[8]),
		.A7(din[7]), .A6(din[6]), .A5(din[5]), .A4(din[4]), .A3(din[3]), .A2(din[2]), .A1(din[1]), .A0(din[0]),

		.B17(1'b0), .B16(1'b0),
		.B15(din[31]), .B14(din[30]), .B13(din[29]), .B12(din[28]), .B11(din[27]), .B10(din[26]), .B9(din[25]), .B8(din[24]),
		.B7(din[23]),.B6(din[22]), .B5(din[21]), .B4(din[20]), .B3(din[19]), .B2(din[18]), .B1(din[17]), .B0(din[16]),

		.C17(1'b0), .C16(1'b0),
		.C15(1'b0), .C14(1'b0), .C13(1'b0), .C12(1'b0), .C11(1'b0), .C10(1'b0), .C9(1'b0), .C8(1'b0),
	    .C7(1'b0), .C6(1'b0), .C5(1'b0), .C4(1'b0), .C3(1'b0), .C2(1'b0), .C1(1'b0), .C0(1'b0),

		.SIGNEDA(1'B0),
		.SIGNEDB(1'B0),
		.SOURCEA(1'B0),
		.SOURCEB(1'B0),

		.P31(dout[31]), .P30(dout[30]), .P29(dout[29]), .P28(dout[28]), .P27(dout[27]), .P26(dout[26]), .P25(dout[25]), .P24(dout[24]),
		.P23(dout[23]), .P22(dout[22]), .P21(dout[21]), .P20(dout[20]), .P19(dout[19]), .P18(dout[18]), .P17(dout[17]), .P16(dout[16]),
		.P15(dout[15]), .P14(dout[14]), .P13(dout[13]), .P12(dout[12]), .P11(dout[11]), .P10(dout[10]), .P9(dout[9]), .P8(dout[8]),
		.P7(dout[7]), .P6(dout[6]), .P5(dout[5]), .P4(dout[4]), .P3(dout[3]), .P2(dout[2]), .P1(dout[1]), .P0(dout[0])
	);


	assign dout_valid = din_valid;
endmodule
