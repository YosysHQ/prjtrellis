module top(input [3:0] di, input ck, input wre, input [3:0] ad, output [3:0] d_o);

SPR16X4C #(.initval ("0xF444")) R1 ( .DI3 (di[3]), .DI2 (di[2]), .DI1 (di[1]), .DI0 (di[0]),
    .CK (ck), .WRE (wre), .AD3 (ad[3]), .AD2 (ad[2]), .AD1 (ad[1]), .AD0 (ad[0]),
    .DO3 (d_o[3]), .DO2 (d_o[2]), .DO1 (d_o[1]), .DO0 (d_o[0]));

endmodule
