module top(input clk, input d, cen, output reg q);
    always @(posedge clk)
        if (!cen)
            q <= d;
endmodule
