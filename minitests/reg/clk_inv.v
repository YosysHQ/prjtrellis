module top(input clk, input d, output reg q);
    always @(negedge clk)
        q <= d;
endmodule
