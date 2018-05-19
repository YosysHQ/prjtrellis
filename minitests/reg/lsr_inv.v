module top(input clk, input d, input r, input s, output q);
    GSR gsr(.GSR(r));
    FD1P3JX ff(.D(d), .SP(1'b0), .PD(!s), .CK(clk), .Q(q));
endmodule
