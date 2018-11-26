module testbench();

	reg clk;

	always #5 clk = (clk === 1'b0);

	initial begin
		$dumpfile("testbench.vcd");
		$dumpvars(0, testbench);

		repeat (10) begin
			repeat (50000) @(posedge clk);
			$display("+50000 cycles");
		end
		$finish;
	end

	wire [7:0] led;

	always @(led) begin
		#1 $display("%b", led);
	end

	attosoc uut (
		.clk      (clk      ),
		.led      (led      )
	);
endmodule
