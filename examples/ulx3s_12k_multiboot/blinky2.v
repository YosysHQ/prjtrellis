module top(input clk, output [7:0] led);
    reg [23:0] cnt = 0;

    always@(posedge clk) begin
        cnt <= cnt + 1;
    end
    assign led[7] = cnt[22];
    assign led[6:0] = 7'b1111111;
endmodule
