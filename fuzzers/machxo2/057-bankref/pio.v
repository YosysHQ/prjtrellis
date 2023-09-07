`define ${dir}

`ifdef NONE

module top(input x);

// Minimum legal empty module
wire dummy;

// Dummy load
GSR gsr_i(.GSR(dummy));

// Dummy source
OSCH osc_i(.OSC(dummy));


endmodule

`else

module top(inout pad);

`ifdef BIDIR

wire dummyo, dummyi;

(* keep *)
(* LOC="${loc}" *)
(* IO_TYPE="${io_type}" *)
${extra_attrs}
BB b_b(.B(pad), .O(dummyo), .I(1'b1), .T(dummyi));

// Dummy load
GSR gsr_i(.GSR(dummyo));

// Dummy source
OSCH osc_i(.OSC(dummyi));

`endif

`ifdef INPUT

wire dummyo;

(* keep *)
(* LOC="${loc}" *)
(* IO_TYPE="${io_type}" *)
${extra_attrs}
IB i_b(.I(pad), .O(dummyo));

// Dummy load
GSR gsr_i(.GSR(dummyo));
BCINRD #(.BANKID("${bank}")) bc(.INRDENI(1'b1));

`endif

`ifdef OUTPUT

(* keep *)
(* LOC="${loc}" *)
(* IO_TYPE="${io_type}" *)
${extra_attrs}
OB o_b(.O(pad), .I(1'b1));

`endif

endmodule

`endif
