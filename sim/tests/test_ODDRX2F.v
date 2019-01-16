`timescale 1ns/1ps
module test_ODDRX2F;
    wire D0, D1, D2, D3;
    reg [3:0] D;
    assign {D3, D2, D1, D0} = D;
    reg RST, ECLK, SCLK;
    wire Q_sim, Q_lat;
    ODDRX2F sim(
		.D0(D0),
		.D1(D1),
		.D2(D2),
		.D3(D3),
		.RST(RST),
		.ECLK(ECLK),
		.SCLK(SCLK),
		.Q(Q_sim));
    ODDRX2F_l lat(
		.D0(D0),
		.D1(D1),
		.D2(D2),
		.D3(D3),
		.RST(RST),
		.ECLK(ECLK),
		.SCLK(SCLK),
		.Q(Q_lat));
    wire diff = Q_lat != Q_sim;
    always begin
	#5 ECLK = 0;
	SCLK = 0;
	#5 ECLK = 1;
	#5 ECLK = 0;
	SCLK = 1;
	#5 ECLK = 1;
    end
    
    integer i;
    initial begin
	$dumpfile("ODDRX2F.vcd");
	$dumpvars;
	D = 4'b0;
	RST = 1'b1;
	#20 RST = 1'b0;
	for(i=0; i<16; i++)
	  @(posedge SCLK) D = i;
	RST = 1'b1;
	for(i=0; i<5; i++)
	  @(posedge SCLK) D = i;
	RST = 1'b0;
	for(i=5; i<12; i++)
	  @(posedge SCLK) D = i;
	RST = 1'b1;
	@(posedge SCLK) RST = 1'b0;
	for(i=0; i<16; i++)
	  @(posedge SCLK) D = i;
	

	#80 $finish;
    end
    

endmodule // test_ODDRX2F
