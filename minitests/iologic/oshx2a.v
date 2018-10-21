module oshx(input [1:0] D, input ECLK, RST, output Q);
wire SCLK;

CLKDIVF #(.DIV("2.0")) cdiv_i (.CLKI(ECLK), .RST(RST), .ALIGNWD(1'b0), .CDIVX(SCLK));

OSHX2A OSHX2A_i(.D0(D[0]), .D1(D[1]),
               .ECLK(ECLK), .SCLK(SCLK), .RST(RST),
               .Q(Q));
endmodule
