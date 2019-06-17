/*
 * Hello world on the ulx3s FTDI serial port at 3000000 baud.
 */
`default_nettype none
`include "uart.v"
`include "pll_120.v"

module top(
	input clk_pin,
	input btn_pin,
	output [7:0] led_pin,
	output gpio0_pin,
	output serial_txd_pin,
	input serial_rxd_pin
);
    wire clk_in;
    wire [7:0] led;
    wire btn;
    wire gpio0;
    wire serial_txd, serial_rxd;

    (* LOC="G2" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("INPUT")) clk_buf (.B(clk_pin), .O(clk_in));

    (* LOC="R1" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("INPUT")) btn_buf (.B(btn_pin), .O(btn));

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
    TRELLIS_IO #(.DIR("OUTPUT")) gpio0_buf (.B(gpio0_pin), .I(gpio0));

    // The FTDI pins are on the ft231x and go to USB port 1
    (* LOC="L4" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("OUTPUT")) ftdi_txd_buf (.B(serial_txd_pin), .I(serial_txd));
    (* LOC="M1" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("INPUT")) ftdi_rxd_buf (.B(serial_rxd_pin), .O(serial_rxd));


    reg [7:0] led_reg;
    assign led = led_reg;

    // Tie GPIO0, keep board from rebooting
    assign gpio0 = 1'b1;

    // Generate a 120 MHz clock from the 25 MHz reference
    wire clk, locked, reset = !locked;
    pll pll_120_i(clk_in, locked, clk);

    // Output data to the serial port
    wire uart_txd_ready;
    reg [7:0] uart_txd;
    reg uart_txd_strobe;

    uart_tx #(.DIVISOR(40)) uart_tx_i(
	.clk(clk),
	.reset(reset),
	.serial(serial_txd),
	.data(uart_txd),
	.ready(uart_txd_ready),
	.data_strobe(uart_txd_strobe),
    );

    reg [23:0] counter;

    always @(posedge clk)
    begin
	uart_txd_strobe <= 0;

	if (uart_txd_ready
	&& !uart_txd_strobe) begin
		uart_txd <= "A" + counter[4:0];
		uart_txd_strobe <= 1;
		counter <= counter + 1;
		led_reg <= counter[23:15];
	end
    end
endmodule
