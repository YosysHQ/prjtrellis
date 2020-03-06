module top(
    input ignore_eclk, ignore_cen, ignore_rst,
    input [3:0] ignore_d,
    output [7:0] ignore_q,
(* IO_TYPE="SSTL18_I" *) input pin_IREG,
(* IO_TYPE="SSTL18_I" *) output pin_OREG,
(* IO_TYPE="SSTL18_I" *) output pin_TSREG,
(* IO_TYPE="SSTL18_I" *) input pin_IDDRX1F,
(* IO_TYPE="SSTL18_I" *) output pin_ODDRX1F,
(* IO_TYPE="SSTL18_I" *) input pin_IDDRX2F,
(* IO_TYPE="SSTL18_I" *) output pin_ODDRX2F
);
    wire ignore_sclk;
    CLKDIVF #(.DIV("2.0")) cdiv_i (.CLKI(ignore_eclk), .RST(ignore_rst), .ALIGNWD(1'b0), .CDIVX(ignore_sclk));

    IFS1P3IX ireg_i (.D(pin_IREG), .SCLK(ignore_sclk), .SP(ignore_cen), .CD(ignore_rst), .Q(ignore_q[0]));
    OFS1P3IX oreg_i (.D(ignore_d[0]), .SCLK(ignore_sclk), .SP(ignore_cen), .CD(ignore_rst), .Q(pin_OREG));
    wire tmp_t;
    OFS1P3IX tsreg_i (.D(ignore_d[0]), .SCLK(ignore_sclk), .SP(ignore_cen), .CD(ignore_rst), .Q(tmp_t));
    assign pin_TSREG = tmp_t ? 1'bz : ignore_d[1];

    IDDRX1F iddr_i(.D(pin_IDDRX1F), .SCLK(ignore_sclk), .RST(ignore_rst), .Q0(ignore_q[1]), .Q1(ignore_q[2]));
    ODDRX1F oddr_i(.Q(pin_ODDRX1F), .SCLK(ignore_sclk), .RST(ignore_rst), .D0(D0), .D1(D1));

    IDDRX2F iddr2_i(.Q0(ignore_q[3]), .Q1(ignore_q[4]), .Q2(ignore_q[5]), .Q3(ignore_q[6]),
                   .ECLK(ignore_eclk), .SCLK(ignore_sclk), .RST(ignore_rst),
                   .D(pin_IDDRX2F));

    ODDRX2F oddr2_i(.D0(ignore_d[0]), .D1(ignore_d[1]), .D2(ignore_d[2]), .D3(ignore_d[3]),
                   .ECLK(ignore_eclk), .SCLK(ignore_sclk), .RST(ignore_rst),
                   .Q(pin_ODDRX2F));
endmodule