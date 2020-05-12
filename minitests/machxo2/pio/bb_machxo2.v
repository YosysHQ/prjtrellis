module top(input pad);

wire dummyo, dummyi;

(* LOC="PB11C" *)
(* IO_TYPE="LVTTL33" *)
BB i_b(.B(pad), .O(dummyo), .I(1'b1), .T(dummyi));

// Dummy load
GSR gsr_i(.GSR(dummyo));

// Dummy source
OSCH osc_i(.OSC(dummyi));

endmodule
