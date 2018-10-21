module top(input clk_pin, input btn_pin, output [7:0] led_pin);

    wire clk;
    wire [7:0] led;
    wire btn;

    (* LOC="A10" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("INPUT")) clk_buf (.B(clk_pin), .O(clk));

    // Pressing and holding SW4 will trigger led array fading
    (* LOC="P4" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("INPUT")) btn_buf (.B(btn_pin), .O(btn));

    (* LOC="B17" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_0 (.B(led_pin[0]), .I(!led[0]));
    (* LOC="A17" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_1 (.B(led_pin[1]), .I(!led[1]));
    (* LOC="C17" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_2 (.B(led_pin[2]), .I(!led[2]));
    (* LOC="B18" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_3 (.B(led_pin[3]), .I(!led[3]));

    (* LOC="A18" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_4 (.B(led_pin[4]), .I(!led[4]));
    (* LOC="B19" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_5 (.B(led_pin[5]), .I(!led[5]));
    (* LOC="A12" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_6 (.B(led_pin[6]), .I(!led[6]));
    (* LOC="A13" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_7 (.B(led_pin[7]), .I(!led[7]));



    localparam ctr_width = 24;
    localparam ctr_max = 2**ctr_width - 1;
    reg [ctr_width-1:0] ctr = 0;
    reg [9:0] pwm_ctr = 0;
    reg dir = 0;

    always@(posedge clk) begin
    ctr <= btn ? ctr : (dir ? ctr - 1'b1 : ctr + 1'b1);
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
endmodule
