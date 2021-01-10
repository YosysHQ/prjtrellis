module top(input clk, d, set, r, output reg q);
    GSR gsr(.GSR(r));
    always @(posedge clk or posedge set)
           if (set)
                q <= 1'b1;
           else
                q <= d;
endmodule
