module top(input set, input reset, input d, output reg q);
    always @(set or reset) begin
        if(reset) begin
            q <= 0;
        end else if(set) begin
            q <= d;
        end
    end
endmodule
