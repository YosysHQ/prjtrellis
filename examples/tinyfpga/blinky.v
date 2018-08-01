module top(input clk_pin, output led_pin);

    wire clk, led;

    (* LOC="B18" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("INPUT")) clk_buf (.B(clk_pin), .O(clk));

    (* LOC="C1" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_0 (.B(led_pin), .I(led));

    reg [23:0] ctr = 0;
    always @(posedge clk)
        ctr <= ctr + 1'b1;

    assign led = ctr[23];

endmodule
