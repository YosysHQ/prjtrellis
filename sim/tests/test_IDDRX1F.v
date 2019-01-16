`timescale 1ns/1ps
module test_IDDRX1F;
    reg D, SCLK, RST;
    wire Q0_sim, Q1_sim;
    wire Q0_lat, Q1_lat;
    wire diff = Q0_sim != Q0_lat || Q1_sim != Q1_lat;

    IDDRX1F sim(
		.D(D),
		.SCLK(SCLK),
		.RST(RST),
		.Q0(Q0_sim),
		.Q1(Q1_sim));
    IDDRX1F_l lat(
		.D(D),
		.SCLK(SCLK),
		.RST(RST),
		.Q0(Q0_lat),
		.Q1(Q1_lat));

    
    initial begin
	$dumpfile("IDDRX1F.vcd");
	$dumpvars;
	SCLK = 0;
	D = 0;
	RST = 0;
	@(posedge SCLK)
	  D = 1;
	@(negedge SCLK)
	  D = 0;
	@(posedge SCLK)
	  D = 1;
	@(negedge SCLK)
	  D = 1;
	@(posedge SCLK)
	  D = 0;
	@(negedge SCLK)
	  D = 1;
	@(posedge SCLK)
	  D = 0;
	@(negedge SCLK)
	  D = 0;
	@(posedge SCLK)
	  RST = 1;
	D = 1;
	@(posedge SCLK)
	  RST = 0;

	@(posedge SCLK);
	@(posedge SCLK);

	$finish;
    end
    always #5 SCLK = ~SCLK;

    
    
	  
endmodule // test_IDDRX1F

