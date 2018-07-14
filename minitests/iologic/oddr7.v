module oddr7(input [6:0] D, input ECLK, RST, output Q);
wire SCLK;

CLKDIVF #(.DIV("3.5")) cdiv_i (.CLKI(ECLK), .RST(RST), .ALIGNWD(1'b0), .CDIVX(SCLK));

ODDR71B oddr_i(.D0(D[0]), .D1(D[1]), .D2(D[2]), .D3(D[3]), .D4(D[4]), .D5(D[5]), .D6(D[6]),
               .ECLK(ECLK), .SCLK(SCLK), .RST(RST),
               .Q(Q));
endmodule
