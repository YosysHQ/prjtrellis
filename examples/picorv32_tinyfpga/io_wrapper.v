module top(
	input clk_pin,
	output led_pin
);

wire clk, led;

reg [17:0] div;

always @(posedge clk)
    div <= div + 1'b1;

(* LOC="B17" *) (* IO_TYPE="LVCMOS33" *)
TRELLIS_IO #(.DIR("INPUT")) clk_buf (.B(clk_pin), .O(clk));

(* LOC="A7" *) (* IO_TYPE="LVCMOS33" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_0 (.B(led_pin), .I(led));

attosoc soc(
	.clk(div[17]),
	.led(led)
);

endmodule
