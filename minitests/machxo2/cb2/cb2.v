module top(input pc0, input pc1, input con, output nc0, output nc1);
    CB2 C1 ( .CI (1'b0), .PC0 (pc0), .PC1 (pc1), .CON (con), .NC0 (nc0), .NC1 (nc1) );
endmodule
