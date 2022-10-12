/*
 * Hello world on the ulx3s FTDI serial port at 3000000 baud.
 */
`default_nettype none
`include "uart.v"
`include "pll_120.v"

module top(
	input clk_25mhz,
	output [7:0] led,
	output wifi_gpio0,
	input ftdi_txd, // from the ftdi chip
	output ftdi_rxd, // to the ftdi chip
);
    // gpio0 must be tied high to prevent board from rebooting
    assign wifi_gpio0 = 1;

    reg [7:0] led_reg;
    assign led = led_reg;

    // Generate a 120 MHz clock from the 25 MHz reference
    wire clk, locked, reset = !locked;
    pll_120 pll_120_i(clk_25mhz, clk, locked);

    // send/recv data at on the FTDI port
    // 120 MHz / 40 == 3 megabaud
    wire uart_txd_ready;
    reg [7:0] uart_txd;
    reg uart_txd_strobe;
    wire uart_rxd_strobe;
    wire [7:0] uart_rxd;

    uart #(.DIVISOR(12500)) uart_i(
	.clk(clk),
	.reset(reset),
	// physical interface
	.serial_txd(ftdi_rxd), // fpga --> ftdi
	.serial_rxd(ftdi_txd), // fpga <-- ftdi
	// logical interface
	.txd(uart_txd),
	.txd_ready(uart_txd_ready),
	.txd_strobe(uart_txd_strobe),
	.rxd(uart_rxd),
	.rxd_strobe(uart_rxd_strobe),
    );

    reg [31:0] counter;

    always @(posedge clk)
    begin
	uart_txd_strobe <= 0;
	counter <= counter + 1;

	if (reset) begin
		counter <= 0;
	end else
	if (uart_rxd_strobe)
	begin
		// echo any input on the serial port back to the serial port
		led_reg <= uart_rxd;
		uart_txd <= uart_rxd;
		uart_txd_strobe <= 1;
	end else
	if (counter[26:0] == 0
	&& uart_txd_ready
	&& !uart_txd_strobe)
	begin
		// periodically print an increasing counter on the serial port
		led_reg <= counter[31:23];
		uart_txd <= "0" + counter[31:27];
		uart_txd_strobe <= 1;
	end
    end
endmodule
