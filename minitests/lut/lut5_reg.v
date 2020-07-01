module top(input a, input b, input c, input d, input e, input clk, output reg q);

wire q_in;

LUT5 #(.init (32'hF4444)) I1 ( .A (a), .B (b), .C (c), .D (d), .E (e), .Z (q_in) );

always @(posedge clk) begin
  q <= q_in;
end

endmodule
