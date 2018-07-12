module top(input CK, SD, SP, D0, D1, output Q);

FL1P3AZ ff(.CK(CK), .SD(SD), .SP(SP), .D0(D0), .D1(D1), .Q(Q));

endmodule
