module top(input clk_pin, output [7:0] led_pin, output [13:0] disp_pin, output clken_pin);

    wire clk;
    wire [7:0] led;
    wire [13:0] disp;
    
    localparam div_n = 25;
    reg clk_div;
    reg [div_n-1:0] div_ctr; 
    
    always @(posedge clk) begin
        div_ctr <= div_ctr + 1'b1;
        clk_div <= (div_ctr == 0);
    end
    
    `include "pattern.vh"
    
    reg [$clog2(pat_len):0] pat_ctr;
    always @ ( posedge clk ) begin
        if (clk_div) begin
            if (pat_ctr == 2*pat_len - 1)
                pat_ctr <= 0;
            else
                pat_ctr <= pat_ctr + 1'b1;
        end
    end
    
    assign led = {clk, ~pat_ctr};
    assign disp = pat_ctr[0] ? 14'h3FFF : ~(display_pat[pat_ctr[$clog2(pat_len):1]]);
    
    // IO buffers
    (* LOC="A4" *) (* IO_TYPE="LVDS" *)
    TRELLIS_IO #(.DIR("INPUT")) clk_buf (.B(clk_pin), .O(clk));

    (* LOC="E16" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_0 (.B(led_pin[0]), .I(led[0]));
    (* LOC="D17" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_1 (.B(led_pin[1]), .I(led[1]));
    (* LOC="D18" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_2 (.B(led_pin[2]), .I(led[2]));
    (* LOC="E18" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_3 (.B(led_pin[3]), .I(led[3]));
    (* LOC="F17" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_4 (.B(led_pin[4]), .I(led[4]));
    (* LOC="F18" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_5 (.B(led_pin[5]), .I(led[5]));
    (* LOC="E17" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_6 (.B(led_pin[6]), .I(led[6]));
    (* LOC="F16" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) led_buf_7 (.B(led_pin[7]), .I(led[7]));

    (* LOC="M20" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) disp_buf_0 (.B(disp_pin[0]), .I(disp[0]));
    (* LOC="L18" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) disp_buf_1 (.B(disp_pin[1]), .I(disp[1]));
    (* LOC="M19" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) disp_buf_2 (.B(disp_pin[2]), .I(disp[2]));
    (* LOC="L16" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) disp_buf_3 (.B(disp_pin[3]), .I(disp[3]));
    (* LOC="L17" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) disp_buf_4 (.B(disp_pin[4]), .I(disp[4]));
    (* LOC="M18" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) disp_buf_5 (.B(disp_pin[5]), .I(disp[5]));
    (* LOC="N16" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) disp_buf_6 (.B(disp_pin[6]), .I(disp[6]));
    (* LOC="M17" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) disp_buf_7 (.B(disp_pin[7]), .I(disp[7]));
    (* LOC="N18" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) disp_buf_8 (.B(disp_pin[8]), .I(disp[8]));
    (* LOC="P17" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) disp_buf_9 (.B(disp_pin[9]), .I(disp[9]));
    (* LOC="N17" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) disp_buf_10 (.B(disp_pin[10]), .I(disp[10]));
    (* LOC="P16" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) disp_buf_11 (.B(disp_pin[11]), .I(disp[11]));
    (* LOC="R16" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) disp_buf_12 (.B(disp_pin[12]), .I(disp[12]));
    (* LOC="R17" *) (* IO_TYPE="LVCMOS25" *)
    TRELLIS_IO #(.DIR("OUTPUT")) disp_buf_13 (.B(disp_pin[13]), .I(disp[13]));
    
    (* LOC="C12" *) (* IO_TYPE="LVCMOS33" *)
    TRELLIS_IO #(.DIR("OUTPUT")) clken_buf (.B(clken_pin), .I(1'b1));
endmodule

