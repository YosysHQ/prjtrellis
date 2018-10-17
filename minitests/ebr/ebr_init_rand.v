module ebr_test(input clk, input [10:0] addr, input [8:0] d, input we, output reg [8:0] q);
    reg [8:0] mem[0:2047];
    
     initial $readmemh("ebr_init_rand.dat", mem);
    always @(posedge clk) begin
        if (we) mem[addr] <= d;
        q <= mem[addr];
    end
endmodule

