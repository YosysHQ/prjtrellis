module top(
    input [2:0] sel,
    input [17:0] A, B, C,
    output [36:0] P_Q,
    input CLK, CEN, RESET, SIGNEDA, SIGNEDB, SOURCEA, SOURCEB
);

wire [36:0] P[0:4];

MULT18X18D #(
    .REG_INPUTA_CLK("NONE"),
    .REG_INPUTA_CE("CE0"),
    .REG_INPUTA_RST("RST0"),
    .REG_INPUTB_CLK("NONE"),
    .REG_INPUTB_CE("CE0"),
    .REG_INPUTB_RST("RST0"),
    .REG_INPUTC_CLK("NONE"),
    .REG_PIPELINE_CLK("NONE"),
    .REG_PIPELINE_CE("CE0"),
    .REG_PIPELINE_RST("RST0"),
    .REG_OUTPUT_CLK("NONE"),
    .CLK0_DIV("ENABLED"),
    .CLK1_DIV("ENABLED"),
    .CLK2_DIV("ENABLED"),
    .CLK3_DIV("ENABLED"),
    .GSR("DISABLED"),
    .SOURCEB_MODE("B_C_DYNAMIC"),
    .RESETMODE("SYNC")
) mult_reg_NONE (
    .A0(A[0]), .A1(A[1]), .A2(A[2]), .A3(A[3]), .A4(A[4]), .A5(A[5]), .A6(A[6]), .A7(A[7]), .A8(A[8]), .A9(A[9]), .A10(A[10]), .A11(A[11]), .A12(A[12]), .A13(A[13]), .A14(A[14]), .A15(A[15]), .A16(A[16]), .A17(A[17]),
    .B0(B[0]), .B1(B[1]), .B2(B[2]), .B3(B[3]), .B4(B[4]), .B5(B[5]), .B6(B[6]), .B7(B[7]), .B8(B[8]), .B9(B[9]), .B10(B[10]), .B11(B[11]), .B12(B[12]), .B13(B[13]), .B14(B[14]), .B15(B[15]), .B16(B[16]), .B17(B[17]),
    .C0(C[0]), .C1(C[1]), .C2(C[2]), .C3(C[3]), .C4(C[4]), .C5(C[5]), .C6(C[6]), .C7(C[7]), .C8(C[8]), .C9(C[9]), .C10(C[10]), .C11(C[11]), .C12(C[12]), .C13(C[13]), .C14(C[14]), .C15(C[15]), .C16(C[16]), .C17(C[17]),
    .SIGNEDA(SIGNEDA), .SIGNEDB(SIGNEDB),
    .CLK0(CLK), .CE0(CEN), .RST0(RESET),
    .P0(P[0][0]), .P1(P[0][1]), .P2(P[0][2]), .P3(P[0][3]), .P4(P[0][4]), .P5(P[0][5]), .P6(P[0][6]), .P7(P[0][7]), .P8(P[0][8]), .P9(P[0][9]), .P10(P[0][10]), .P11(P[0][11]), .P12(P[0][12]), .P13(P[0][13]), .P14(P[0][14]), .P15(P[0][15]), .P16(P[0][16]), .P17(P[0][17]), .P18(P[0][18]), .P19(P[0][19]), .P20(P[0][20]), .P21(P[0][21]), .P22(P[0][22]), .P23(P[0][23]), .P24(P[0][24]), .P25(P[0][25]), .P26(P[0][26]), .P27(P[0][27]), .P28(P[0][28]), .P29(P[0][29]), .P30(P[0][30]), .P31(P[0][31]), .P32(P[0][32]), .P33(P[0][33]), .P34(P[0][34]), .P35(P[0][35]),
    .SIGNEDP()
);

MULT18X18D #(
    .REG_INPUTA_CLK("NONE"),
    .REG_INPUTA_CE("CE0"),
    .REG_INPUTA_RST("RST0"),
    .REG_INPUTB_CLK("NONE"),
    .REG_INPUTB_CE("CE0"),
    .REG_INPUTB_RST("RST0"),
    .REG_INPUTC_CLK("NONE"),
    .REG_PIPELINE_CLK("NONE"),
    .REG_PIPELINE_CE("CE0"),
    .REG_PIPELINE_RST("RST0"),
    .REG_OUTPUT_CLK("CLK0"),
    .CLK0_DIV("ENABLED"),
    .CLK1_DIV("ENABLED"),
    .CLK2_DIV("ENABLED"),
    .CLK3_DIV("ENABLED"),
    .GSR("DISABLED"),
    .SOURCEB_MODE("B_C_DYNAMIC"),
    .RESETMODE("SYNC")
) mult_reg_OUTPUT (
    .A0(A[0]), .A1(A[1]), .A2(A[2]), .A3(A[3]), .A4(A[4]), .A5(A[5]), .A6(A[6]), .A7(A[7]), .A8(A[8]), .A9(A[9]), .A10(A[10]), .A11(A[11]), .A12(A[12]), .A13(A[13]), .A14(A[14]), .A15(A[15]), .A16(A[16]), .A17(A[17]),
    .B0(B[0]), .B1(B[1]), .B2(B[2]), .B3(B[3]), .B4(B[4]), .B5(B[5]), .B6(B[6]), .B7(B[7]), .B8(B[8]), .B9(B[9]), .B10(B[10]), .B11(B[11]), .B12(B[12]), .B13(B[13]), .B14(B[14]), .B15(B[15]), .B16(B[16]), .B17(B[17]),
    .C0(C[0]), .C1(C[1]), .C2(C[2]), .C3(C[3]), .C4(C[4]), .C5(C[5]), .C6(C[6]), .C7(C[7]), .C8(C[8]), .C9(C[9]), .C10(C[10]), .C11(C[11]), .C12(C[12]), .C13(C[13]), .C14(C[14]), .C15(C[15]), .C16(C[16]), .C17(C[17]),
    .SIGNEDA(SIGNEDA), .SIGNEDB(SIGNEDB),
    .CLK0(CLK), .CE0(CEN), .RST0(RESET),
    .P0(P[1][0]), .P1(P[1][1]), .P2(P[1][2]), .P3(P[1][3]), .P4(P[1][4]), .P5(P[1][5]), .P6(P[1][6]), .P7(P[1][7]), .P8(P[1][8]), .P9(P[1][9]), .P10(P[1][10]), .P11(P[1][11]), .P12(P[1][12]), .P13(P[1][13]), .P14(P[1][14]), .P15(P[1][15]), .P16(P[1][16]), .P17(P[1][17]), .P18(P[1][18]), .P19(P[1][19]), .P20(P[1][20]), .P21(P[1][21]), .P22(P[1][22]), .P23(P[1][23]), .P24(P[1][24]), .P25(P[1][25]), .P26(P[1][26]), .P27(P[1][27]), .P28(P[1][28]), .P29(P[1][29]), .P30(P[1][30]), .P31(P[1][31]), .P32(P[1][32]), .P33(P[1][33]), .P34(P[1][34]), .P35(P[1][35]),
    .SIGNEDP()
);

MULT18X18D #(
    .REG_INPUTA_CLK("CLK0"),
    .REG_INPUTA_CE("CE0"),
    .REG_INPUTA_RST("RST0"),
    .REG_INPUTB_CLK("CLK0"),
    .REG_INPUTB_CE("CE0"),
    .REG_INPUTB_RST("RST0"),
    .REG_INPUTC_CLK("CLK0"),
    .REG_PIPELINE_CLK("NONE"),
    .REG_PIPELINE_CE("CE0"),
    .REG_PIPELINE_RST("RST0"),
    .REG_OUTPUT_CLK("NONE"),
    .CLK0_DIV("ENABLED"),
    .CLK1_DIV("ENABLED"),
    .CLK2_DIV("ENABLED"),
    .CLK3_DIV("ENABLED"),
    .GSR("DISABLED"),
    .SOURCEB_MODE("B_C_DYNAMIC"),
    .RESETMODE("SYNC")
) mult_reg_INPUT (
    .A0(A[0]), .A1(A[1]), .A2(A[2]), .A3(A[3]), .A4(A[4]), .A5(A[5]), .A6(A[6]), .A7(A[7]), .A8(A[8]), .A9(A[9]), .A10(A[10]), .A11(A[11]), .A12(A[12]), .A13(A[13]), .A14(A[14]), .A15(A[15]), .A16(A[16]), .A17(A[17]),
    .B0(B[0]), .B1(B[1]), .B2(B[2]), .B3(B[3]), .B4(B[4]), .B5(B[5]), .B6(B[6]), .B7(B[7]), .B8(B[8]), .B9(B[9]), .B10(B[10]), .B11(B[11]), .B12(B[12]), .B13(B[13]), .B14(B[14]), .B15(B[15]), .B16(B[16]), .B17(B[17]),
    .C0(C[0]), .C1(C[1]), .C2(C[2]), .C3(C[3]), .C4(C[4]), .C5(C[5]), .C6(C[6]), .C7(C[7]), .C8(C[8]), .C9(C[9]), .C10(C[10]), .C11(C[11]), .C12(C[12]), .C13(C[13]), .C14(C[14]), .C15(C[15]), .C16(C[16]), .C17(C[17]),
    .SIGNEDA(SIGNEDA), .SIGNEDB(SIGNEDB),
    .CLK0(CLK), .CE0(CEN), .RST0(RESET),
    .P0(P[2][0]), .P1(P[2][1]), .P2(P[2][2]), .P3(P[2][3]), .P4(P[2][4]), .P5(P[2][5]), .P6(P[2][6]), .P7(P[2][7]), .P8(P[2][8]), .P9(P[2][9]), .P10(P[2][10]), .P11(P[2][11]), .P12(P[2][12]), .P13(P[2][13]), .P14(P[2][14]), .P15(P[2][15]), .P16(P[2][16]), .P17(P[2][17]), .P18(P[2][18]), .P19(P[2][19]), .P20(P[2][20]), .P21(P[2][21]), .P22(P[2][22]), .P23(P[2][23]), .P24(P[2][24]), .P25(P[2][25]), .P26(P[2][26]), .P27(P[2][27]), .P28(P[2][28]), .P29(P[2][29]), .P30(P[2][30]), .P31(P[2][31]), .P32(P[2][32]), .P33(P[2][33]), .P34(P[2][34]), .P35(P[2][35]),
    .SIGNEDP()
);

MULT18X18D #(
    .REG_INPUTA_CLK("NONE"),
    .REG_INPUTA_CE("CE0"),
    .REG_INPUTA_RST("RST0"),
    .REG_INPUTB_CLK("NONE"),
    .REG_INPUTB_CE("CE0"),
    .REG_INPUTB_RST("RST0"),
    .REG_INPUTC_CLK("NONE"),
    .REG_PIPELINE_CLK("CLK0"),
    .REG_PIPELINE_CE("CE0"),
    .REG_PIPELINE_RST("RST0"),
    .REG_OUTPUT_CLK("NONE"),
    .CLK0_DIV("ENABLED"),
    .CLK1_DIV("ENABLED"),
    .CLK2_DIV("ENABLED"),
    .CLK3_DIV("ENABLED"),
    .GSR("DISABLED"),
    .SOURCEB_MODE("B_C_DYNAMIC"),
    .RESETMODE("SYNC")
) mult_reg_PIPELINE (
    .A0(A[0]), .A1(A[1]), .A2(A[2]), .A3(A[3]), .A4(A[4]), .A5(A[5]), .A6(A[6]), .A7(A[7]), .A8(A[8]), .A9(A[9]), .A10(A[10]), .A11(A[11]), .A12(A[12]), .A13(A[13]), .A14(A[14]), .A15(A[15]), .A16(A[16]), .A17(A[17]),
    .B0(B[0]), .B1(B[1]), .B2(B[2]), .B3(B[3]), .B4(B[4]), .B5(B[5]), .B6(B[6]), .B7(B[7]), .B8(B[8]), .B9(B[9]), .B10(B[10]), .B11(B[11]), .B12(B[12]), .B13(B[13]), .B14(B[14]), .B15(B[15]), .B16(B[16]), .B17(B[17]),
    .C0(C[0]), .C1(C[1]), .C2(C[2]), .C3(C[3]), .C4(C[4]), .C5(C[5]), .C6(C[6]), .C7(C[7]), .C8(C[8]), .C9(C[9]), .C10(C[10]), .C11(C[11]), .C12(C[12]), .C13(C[13]), .C14(C[14]), .C15(C[15]), .C16(C[16]), .C17(C[17]),
    .SIGNEDA(SIGNEDA), .SIGNEDB(SIGNEDB),
    .CLK0(CLK), .CE0(CEN), .RST0(RESET),
    .P0(P[3][0]), .P1(P[3][1]), .P2(P[3][2]), .P3(P[3][3]), .P4(P[3][4]), .P5(P[3][5]), .P6(P[3][6]), .P7(P[3][7]), .P8(P[3][8]), .P9(P[3][9]), .P10(P[3][10]), .P11(P[3][11]), .P12(P[3][12]), .P13(P[3][13]), .P14(P[3][14]), .P15(P[3][15]), .P16(P[3][16]), .P17(P[3][17]), .P18(P[3][18]), .P19(P[3][19]), .P20(P[3][20]), .P21(P[3][21]), .P22(P[3][22]), .P23(P[3][23]), .P24(P[3][24]), .P25(P[3][25]), .P26(P[3][26]), .P27(P[3][27]), .P28(P[3][28]), .P29(P[3][29]), .P30(P[3][30]), .P31(P[3][31]), .P32(P[3][32]), .P33(P[3][33]), .P34(P[3][34]), .P35(P[3][35]),
    .SIGNEDP()
);


MULT18X18D #(
    .REG_INPUTA_CLK("CLK0"),
    .REG_INPUTA_CE("CE0"),
    .REG_INPUTA_RST("RST0"),
    .REG_INPUTB_CLK("CLK0"),
    .REG_INPUTB_CE("CE0"),
    .REG_INPUTB_RST("RST0"),
    .REG_INPUTC_CLK("CLK0"),
    .REG_PIPELINE_CLK("CLK0"),
    .REG_PIPELINE_CE("CE0"),
    .REG_PIPELINE_RST("RST0"),
    .REG_OUTPUT_CLK("CLK0"),
    .CLK0_DIV("ENABLED"),
    .CLK1_DIV("ENABLED"),
    .CLK2_DIV("ENABLED"),
    .CLK3_DIV("ENABLED"),
    .GSR("DISABLED"),
    .SOURCEB_MODE("B_C_DYNAMIC"),
    .RESETMODE("SYNC")
) mult_reg_ALL (
    .A0(A[0]), .A1(A[1]), .A2(A[2]), .A3(A[3]), .A4(A[4]), .A5(A[5]), .A6(A[6]), .A7(A[7]), .A8(A[8]), .A9(A[9]), .A10(A[10]), .A11(A[11]), .A12(A[12]), .A13(A[13]), .A14(A[14]), .A15(A[15]), .A16(A[16]), .A17(A[17]),
    .B0(B[0]), .B1(B[1]), .B2(B[2]), .B3(B[3]), .B4(B[4]), .B5(B[5]), .B6(B[6]), .B7(B[7]), .B8(B[8]), .B9(B[9]), .B10(B[10]), .B11(B[11]), .B12(B[12]), .B13(B[13]), .B14(B[14]), .B15(B[15]), .B16(B[16]), .B17(B[17]),
    .C0(C[0]), .C1(C[1]), .C2(C[2]), .C3(C[3]), .C4(C[4]), .C5(C[5]), .C6(C[6]), .C7(C[7]), .C8(C[8]), .C9(C[9]), .C10(C[10]), .C11(C[11]), .C12(C[12]), .C13(C[13]), .C14(C[14]), .C15(C[15]), .C16(C[16]), .C17(C[17]),
    .SIGNEDA(SIGNEDA), .SIGNEDB(SIGNEDB),
    .CLK0(CLK), .CE0(CEN), .RST0(RESET),
    .P0(P[4][0]), .P1(P[4][1]), .P2(P[4][2]), .P3(P[4][3]), .P4(P[4][4]), .P5(P[4][5]), .P6(P[4][6]), .P7(P[4][7]), .P8(P[4][8]), .P9(P[4][9]), .P10(P[4][10]), .P11(P[4][11]), .P12(P[4][12]), .P13(P[4][13]), .P14(P[4][14]), .P15(P[4][15]), .P16(P[4][16]), .P17(P[4][17]), .P18(P[4][18]), .P19(P[4][19]), .P20(P[4][20]), .P21(P[4][21]), .P22(P[4][22]), .P23(P[4][23]), .P24(P[4][24]), .P25(P[4][25]), .P26(P[4][26]), .P27(P[4][27]), .P28(P[4][28]), .P29(P[4][29]), .P30(P[4][30]), .P31(P[4][31]), .P32(P[4][32]), .P33(P[4][33]), .P34(P[4][34]), .P35(P[4][35]),
    .SIGNEDP()
);


assign P_Q = P[sel];


endmodule