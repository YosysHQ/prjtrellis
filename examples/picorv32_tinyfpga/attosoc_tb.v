module testbench();

	reg clk;

	always #5 clk = (clk === 1'b0);

	initial begin
		$dumpfile("testbench.vcd");
		$dumpvars(0, testbench);

		repeat (10) begin
			repeat (256) @(posedge clk);
			$display("+256 cycles");
		end
		$finish;
	end

	wire led;

	always @(led) begin
		#1 $display("%b", clk);
	end

	attosoc uut (
		.clk      (clk      ),
		.led      (led      )
	);
endmodule
