module top(input clk, d, set, output reg q);
    always @(posedge clk or posedge set)
           if (set)
                q <= 1'b1;
           else
                q <= d;
endmodule
