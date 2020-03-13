module oddr7(input D, input ECLK, RST, output [3:0] Q);
wire SCLK;

CLKDIVF #(.DIV("2.0")) cdiv_i (.CLKI(ECLK), .RST(RST), .ALIGNWD(1'b0), .CDIVX(SCLK));

IDDRX2F oddr_i(.Q0(Q[0]), .Q1(Q[1]), .Q2(Q[2]), .Q3(Q[3]),
               .ECLK(ECLK), .SCLK(SCLK), .RST(RST),
               .D(D));
endmodule
