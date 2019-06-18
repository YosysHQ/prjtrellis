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
    pll_120 pll_120_i(clk_25mhz, locked, clk);

    // Output data to the serial port
    wire uart_txd_ready;
    reg [7:0] uart_txd;
    reg uart_txd_strobe;

    uart_tx #(.DIVISOR(40)) uart_tx_i(
	.clk(clk),
	.reset(reset),
	.serial(ftdi_rxd), // fpga --> ftdi
	.data(uart_txd),
	.ready(uart_txd_ready),
	.data_strobe(uart_txd_strobe),
    );

    // input from the serial port
    wire uart_rxd_strobe;
    wire [7:0] uart_rxd;

    uart_rx #(.DIVISOR(10)) uart_rx_i(
	.clk(clk),
	.reset(reset),
	.serial(ftdi_txd), // fpga <-- ftdi
	.data(uart_rxd),
	.data_strobe(uart_rxd_strobe),
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
