module top(input [17:0] a, input [17:0] b, input [35:0] c, output [35:0] q);
	
	(* syn_multstyle="block_mult" *)
	wire [35:0] product = a * b;
	assign q = product + c;

endmodule

