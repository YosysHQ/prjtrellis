module top(input clk, d, set, cen, output reg q);
    always @(posedge clk)
           if (cen)
               if (set)
                    q <= 1'b1;
               else
                    q <= d;
endmodule
