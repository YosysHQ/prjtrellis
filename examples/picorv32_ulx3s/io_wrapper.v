module top(
	input clk_pin,
	output [7:0] led_pin,
	output gpio0_pin
);

wire clk;
wire [7:0] led;

reg [1:0] divclk;

always @(posedge clk)
    divclk <= divclk + 1'b1;

(* LOC="G2" *) (* IO_TYPE="LVCMOS33" *)
TRELLIS_IO #(.DIR("INPUT")) clk_buf (.B(clk_pin), .O(clk));

(* LOC="B2" *) (* IO_TYPE="LVCMOS33" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_0 (.B(led_pin[0]), .I(led[0]));
(* LOC="C2" *) (* IO_TYPE="LVCMOS33" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_1 (.B(led_pin[1]), .I(led[1]));
(* LOC="C1" *) (* IO_TYPE="LVCMOS33" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_2 (.B(led_pin[2]), .I(led[2]));
(* LOC="D2" *) (* IO_TYPE="LVCMOS33" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_3 (.B(led_pin[3]), .I(led[3]));

(* LOC="D1" *) (* IO_TYPE="LVCMOS33" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_4 (.B(led_pin[4]), .I(led[4]));
(* LOC="E2" *) (* IO_TYPE="LVCMOS33" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_5 (.B(led_pin[5]), .I(led[5]));
(* LOC="E1" *) (* IO_TYPE="LVCMOS33" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_6 (.B(led_pin[6]), .I(led[6]));
(* LOC="H3" *) (* IO_TYPE="LVCMOS33" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_7 (.B(led_pin[7]), .I(led[7]));

(* LOC="L2" *) (* IO_TYPE="LVCMOS33" *)
TRELLIS_IO #(.DIR("OUTPUT")) gpio0_buf (.B(gpio0_pin), .I(1'b1));

attosoc soc(
	.clk(divclk[1]),
	.led(led)
);

endmodule
