module idelay(input D, MOVE, LOADN, DIR, output Q, CFLAG);
wire dly_out;
DELAYF dly_f (.A(D), .MOVE(MOVE), .LOADN(LOADN), .DIRECTION(DIR), .Z(dly_out), .CFLAG(CFLAG));
assign Q = ~dly_out;
endmodule

