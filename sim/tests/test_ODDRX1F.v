`timescale 1ns/1ps
module test_ODDRX1F;
    reg D0, D1, SCLK, RST;
    wire sim_Q, lat_Q;

    wire diff = sim_Q !== lat_Q;

    ODDRX1F sim(/*AUTOINST*/
		// Outputs
		.Q			(sim_Q),
		// Inputs
		.D0			(D0),
		.D1			(D1),
		.SCLK			(SCLK),
		.RST			(RST));
    ODDRX1F_l lattice(/*AUTOINST*/
		      // Outputs
		      .Q			(lat_Q),
		      // Inputs
		      .D0			(D0),
		      .D1			(D1),
		      .SCLK			(SCLK),
		      .RST			(RST));
    initial begin
	$dumpfile("ODDRX1F.vcd");
	$dumpvars;
	#200 $finish;
    end

    initial begin
	SCLK = 1;
	RST = 0;
	D0 = 0;
	D1 = 0;
	#10 RST = 0;
	#10 RST = 0;
	#10 D0 = 1;
	#10 D1 = 1;
	#10 D0 = 0;
	#20 RST = 1;
	#10 RST = 0;
	#20 RST = 1;
	#10 RST = 0;
    end
    

    always #5 SCLK <= ~SCLK; 
      

endmodule // test_ODDRX1F

// Local Variables:
// verilog-library-flags:("-y ../ -y../lattice")
// End:
