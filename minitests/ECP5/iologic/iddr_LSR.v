module iddr(input [3:0] D, SCLK, RST, output [3:0] Q0, Q1);
IDDRX1F iddr_i0(.D(D[0]), .SCLK(SCLK), .RST(RST), .Q0(Q0[0]), .Q1(Q1[0]));
IDDRX1F iddr_i1(.D(D[1]), .SCLK(SCLK), .RST(!RST), .Q0(Q0[1]), .Q1(Q1[1]));
IDDRX1F iddr_i2(.D(D[2]), .SCLK(SCLK), .RST(RST||Q0[0]), .Q0(Q0[2]), .Q1(Q1[2]));
endmodule

