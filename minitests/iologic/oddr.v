module oddr(output Q, input SCLK, RST, D0, D1);
ODDRX1F oddr_i(.Q(Q), .SCLK(SCLK), .RST(RST), .D0(D0), .D1(D1));
endmodule

