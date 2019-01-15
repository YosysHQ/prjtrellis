`timescale 1ns/1ps
module ODDRX1F(/*AUTOARG*/
    // Outputs
    Q,
    // Inputs
    D0, D1, SCLK, RST
    );

    input D0, D1, SCLK, RST;
    output Q;

    parameter GSR = "ENABLED";
    wire   gsr, pur;
    gsr_pur_assign gsr_inst(gsr, pur);
    reg   sr;
    always @(*)
      if(GSR == "ENABLED")
	sr = !(gsr && pur);
      else
	sr = !pur;

    wire   rst_internal;
    assign rst_internal = RST | sr;
      


    assign Q = SCLK ? pipe_3[1] : pipe_3[0];

    reg [1:0] pipe_1, pipe_2, pipe_3;
    always @(posedge SCLK or rst_internal) begin
	if(rst_internal) begin
	    /*AUTORESET*/
	    // Beginning of autoreset for uninitialized flops
	    pipe_1 <= 2'h0;
	    pipe_2 <= 2'h0;
	    pipe_3 <= 2'h0;
	    // End of automatics
	end
	
	else if(SCLK == 1) begin
	    pipe_1 <= {D0, D1};
	    pipe_2 <= pipe_1;
	    pipe_3 <= pipe_2;
	end
    end

endmodule // ODDRX1F
