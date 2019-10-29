module top(
	input clk_25mhz,
	input [6:0] btn,
	output [7:0] led,
	output wifi_gpio0
);
    wire clk = clk_25mhz;
    wire button = btn[1]; // FIRE1

    localparam ctr_width = 24;
    localparam ctr_max = 2**ctr_width - 1;
    reg [ctr_width-1:0] ctr = 0;
    reg [9:0] pwm_ctr = 0;
    reg dir = 0;

    always@(posedge clk) begin
    ctr <= button ? ctr : (dir ? ctr - 1'b1 : ctr + 1'b1);
        if (ctr[ctr_width-1 : ctr_width-3] == 0 && dir == 1)
            dir <= 1'b0;
        else if (ctr[ctr_width-1 : ctr_width-3] == 7 && dir == 0)
            dir <= 1'b1;
        pwm_ctr <= pwm_ctr + 1'b1;
    end

    reg [9:0] brightness [0:7];
    localparam bright_max = 2**10 - 1;
    reg [7:0] led_reg;

    genvar i;
    generate
    for (i = 0; i < 8; i=i+1) begin
       always @ (posedge clk) begin
            if (ctr[ctr_width-1 : ctr_width-3] == i)
                brightness[i] <= bright_max;
            else if (ctr[ctr_width-1 : ctr_width-3] == (i - 1))
                brightness[i] <= ctr[ctr_width-4:ctr_width-13];
             else if (ctr[ctr_width-1 : ctr_width-3] == (i + 1))
                 brightness[i] <= bright_max - ctr[ctr_width-4:ctr_width-13];
            else
                brightness[i] <= 0;
            led_reg[i] <= pwm_ctr < brightness[i];
       end
    end
    endgenerate

    assign led = led_reg;

    // Tie GPIO0, keep board from rebooting
    assign wifi_gpio0 = 1'b1;

endmodule
