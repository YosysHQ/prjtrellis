module iddr(input D, SCLK, RST, output Q0, Q1);
IDDRX1F iddr_i(.D(D), .SCLK(SCLK), .RST(RST), .Q0(Q0), .Q1(Q1));
endmodule

