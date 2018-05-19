module top(input clk, d, reset, output reg q);
    initial q = 1'b1;
    always @(posedge clk)
           if (reset)
                q <= 1'b0;
           else
                q <= d;
endmodule
