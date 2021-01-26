module top(input clk, d, set, reset, cen, output reg q);
    always @(posedge clk or posedge set or posedge reset)
           if (set)
              q <= 1'b1;
           else if(reset)
              q <= 1'b0;
           else if(cen)
                q <= d;
endmodule
