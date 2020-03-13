module top(
    input ignore_t,
    input ignore_i,
    output [11:0] ignore_o,
(* IO_TYPE="LVCMOS33" *) inout io_LVCMOS33,
(* IO_TYPE="LVCMOS25" *) inout io_LVCMOS25,
(* IO_TYPE="LVCMOS18" *) inout io_LVCMOS18,
(* IO_TYPE="LVCMOS15" *) inout io_LVCMOS15,
(* IO_TYPE="LVCMOS12" *) inout io_LVCMOS12,

(* IO_TYPE="LVDS" *) inout io_LVDS,
(* IO_TYPE="SSTL18_I" *) inout io_SSTL18_I,
(* IO_TYPE="SSTL18_II" *) inout io_SSTL18_II,
(* IO_TYPE="SSTL15_I" *) inout io_SSTL15_I,
(* IO_TYPE="SSTL15_II" *) inout io_SSTL15_II

);

    assign io_LVCMOS33 = ignore_t ? 1'bz : ignore_i;
    assign ignore_o[0] = io_LVCMOS33;

    assign io_LVCMOS25 = ignore_t ? 1'bz : ignore_i;
    assign ignore_o[1] = io_LVCMOS25;

    assign io_LVCMOS18 = ignore_t ? 1'bz : ignore_i;
    assign ignore_o[2] = io_LVCMOS18;

    assign io_LVCMOS15 = ignore_t ? 1'bz : ignore_i;
    assign ignore_o[3] = io_LVCMOS15;

    assign io_LVCMOS12 = ignore_t ? 1'bz : ignore_i;
    assign ignore_o[4] = io_LVCMOS12;

    assign io_LVDS = ignore_t ? 1'bz : ignore_i;
    assign ignore_o[5] = io_LVDS;

    assign io_SSTL18_I = ignore_t ? 1'bz : ignore_i;
    assign ignore_o[6] = io_SSTL18_I;

    assign io_SSTL18_II = ignore_t ? 1'bz : ignore_i;
    assign ignore_o[7] = io_SSTL18_II;

    assign io_SSTL15_I = ignore_t ? 1'bz : ignore_i;
    assign ignore_o[8] = io_SSTL15_I;

    assign io_SSTL15_II = ignore_t ? 1'bz : ignore_i;
    assign ignore_o[9] = io_SSTL15_II;

endmodule