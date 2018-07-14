module ebr_test(input clk, input [9:0] addr, input [8:0] d, input we, output reg [8:0] q);
    reg [8:0] mem[0:1023];
    
    always @(posedge clk) begin
        if (we) mem[addr] <= d;
        q <= mem[addr];
    end
endmodule

