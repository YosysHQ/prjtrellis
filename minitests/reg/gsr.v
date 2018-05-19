module top(input clk, input d, input r, output q);
    GSR gsr(.GSR(r));
    FD1P3AX ff(.D(d), .SP(1'b1), .CK(clk), .Q(q));
endmodule
