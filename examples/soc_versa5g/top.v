module top(
    input clkin,
    output [7:0] led,
    output uart_tx,
    input uart_rx,
);

wire clk;
wire [7:0] int_led;

pll_100_50 pll(
    .clki(clkin),
    .clko(clk)
);

attosoc soc(
    .clk(clk),
    .led(int_led),
    .uart_tx(uart_tx),
    .uart_rx(uart_rx)
);

assign led = ~int_led;
endmodule
