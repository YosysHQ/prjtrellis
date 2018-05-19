module top(input clk, d, set, output reg q);
    always @(posedge clk)
           if (!set)
                q <= 1'b1;
           else
                q <= d;
endmodule
