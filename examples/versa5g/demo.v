module top(input clk, output [7:0] led, output [13:0] disp);

    
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


endmodule

