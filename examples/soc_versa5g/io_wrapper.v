module top(
	input clk_pin,
	output [7:0] led_pin,
        output clken_pin
);

wire clk;
wire [7:0] led;

reg [4:0] divclk;

always @(posedge clk)
    divclk <= divclk + 1'b1;

// IO buffers
(* LOC="A4" *) (* IO_TYPE="LVDS" *)
TRELLIS_IO #(.DIR("INPUT")) clk_buf (.B(clk_pin), .O(clk));

(* LOC="E16" *) (* IO_TYPE="LVCMOS25" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_0 (.B(led_pin[0]), .I(!led[0]));
(* LOC="D17" *) (* IO_TYPE="LVCMOS25" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_1 (.B(led_pin[1]), .I(!led[1]));
(* LOC="D18" *) (* IO_TYPE="LVCMOS25" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_2 (.B(led_pin[2]), .I(!led[2]));
(* LOC="E18" *) (* IO_TYPE="LVCMOS25" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_3 (.B(led_pin[3]), .I(!led[3]));
(* LOC="F17" *) (* IO_TYPE="LVCMOS25" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_4 (.B(led_pin[4]), .I(!led[4]));
(* LOC="F18" *) (* IO_TYPE="LVCMOS25" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_5 (.B(led_pin[5]), .I(!led[5]));
(* LOC="E17" *) (* IO_TYPE="LVCMOS25" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_6 (.B(led_pin[6]), .I(!led[6]));
(* LOC="F16" *) (* IO_TYPE="LVCMOS25" *)
TRELLIS_IO #(.DIR("OUTPUT")) led_buf_7 (.B(led_pin[7]), .I(!led[7]));

(* LOC="C12" *) (* IO_TYPE="LVCMOS33" *)
TRELLIS_IO #(.DIR("OUTPUT")) clken_buf (.B(clken_pin), .I(1'b1));


attosoc soc(
	.clk(divclk[4]),
	.led(led)
);


endmodule
