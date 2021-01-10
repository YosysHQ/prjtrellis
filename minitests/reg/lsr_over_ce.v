module top(input clk, d, set, cen, output reg q);
    always @(posedge clk)
         if (set)
            q <= 1'b1;
         else
             if (cen)
                  q <= d;
endmodule
