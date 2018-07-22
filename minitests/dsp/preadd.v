module top(input [8:0] a, input [8:0] b, input [8:0] c, output [17:0] q);
wire [8:0] add = a + b;
(* syn_multstyle = "block_mult" *)
wire [17:0] res = add * c;
assign q = res;
endmodule

