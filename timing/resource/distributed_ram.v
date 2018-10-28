module top(
    input [3:0] di,
    input wck,
    input wre0, wre1,
    input [3:0] rad,
    input [3:0] wad,
    output [3:0] q,
    input rck,
    output [3:0] qq
);
    DPR16X4C ram_0 (
        .DI0(di[0]), .DI1(di[1]), .DI2(di[2]), .DI3(di[3]),
        .WCK(wck), .WRE(wre0),
        .RAD0(rad[0]), .RAD1(rad[1]), .RAD2(rad[2]), .RAD3(rad[3]),
        .WAD0(rad[0]), .WAD1(rad[1]), .WAD2(rad[2]), .WAD3(rad[3]),
        .Q0(q[0]), .Q1(q[1]), .Q2(q[2]), .Q3(q[3])
    );

    wire [3:0] qp;
    DPR16X4C ram_1 (
    .DI0(di[0]), .DI1(di[1]), .DI2(di[2]), .DI3(di[3]),
    .WCK(wck), .WRE(wre1),
    .RAD0(rad[0]), .RAD1(rad[1]), .RAD2(rad[2]), .RAD3(rad[3]),
    .WAD0(rad[0]), .WAD1(rad[1]), .WAD2(rad[2]), .WAD3(rad[3]),
    .Q0(qp[0]), .Q1(qp[1]), .Q2(qp[2]), .Q3(qp[3])
    );

    always @(posedge rck)
        qq <= qp;
endmodule