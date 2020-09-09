module top(input a, input b, input c, input d, input clk, output reg q);

wire q_in;

LUT4 #(.init (32'hF444)) I1 ( .A (a), .B (b), .C (c), .D (d), .Z (q_in) );

always @(posedge clk) begin
  q <= q_in;
end

endmodule
