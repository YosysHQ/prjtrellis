module top (
	input clk,
	input [31:0] a,
	input [31:0] b,
    input [7:0] c,

	output reg [63:0] d
);

    reg [63:0] tmp;
	always @(posedge clk) begin
        tmp <= tmp + 123323;
		d <= (a + b) * c + tmp;
	end
    
endmodule
