module top(input pad);

(* LOC="P4" *)
(* IO_TYPE="LVTTL33" *)
IB i_b(.I(pad), .O(dummy));

// Dummy load
GSR gsr_i(.GSR(dummy));

endmodule
