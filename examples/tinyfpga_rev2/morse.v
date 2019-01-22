module top(input clk, output led);

	// HELLO
	// .... . .-.. .-.. ---
    // 10101 000 1 000 101110101 000 101110101 000 11101110111 00000000
	localparam pattern_len = 55;
	localparam pattern = 55'b00000000_11101110111_000_101011101_000_101011101_000_1_000_10101;

	reg [21:0] div = 0;

	always @ ( posedge clk ) begin
		div <= div + 1'b1;
	end

	reg [5:0] ctr = 0;
	always @(posedge clk) begin
		if (div == 0) begin
			if (ctr == pattern_len - 1) begin
				ctr <= 0;
			end else begin
				ctr <= ctr + 1'b1;
			end
		end
	end

	assign led = pattern[ctr];

endmodule
