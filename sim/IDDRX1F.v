`timescale 1ns/1ps
module IDDRX1F(/*AUTOARG*/
    // Outputs
    Q0, Q1,
    // Inputs
    D, SCLK, RST
    );
    input D, SCLK, RST;
    output reg Q0, Q1;
    initial
      {Q0, Q1} = 2'b0;

    reg [1:0] pipe_1;

    parameter GSR = "ENABLED";
    wire   gsr, pur;
    gsr_pur_assign gsr_inst(gsr, pur);
    reg   sr;
    always @(*)
      if(GSR == "ENABLED")
	sr = !(gsr && pur);
      else
	sr = !pur;
    wire  rst_internal = RST || sr;

    reg   last_clock;
    always @(SCLK)
      last_clock <= SCLK;

    
    always @(SCLK or rst_internal) begin
	if(rst_internal == 1'b1) begin
	    pipe_1 <= 2'b0;
	end
	else if(SCLK === 1'b1 && last_clock === 1'b0) begin
	    pipe_1[0] <= D;
	    {Q1, Q0} <= pipe_1;
	end
	
	else if(SCLK === 1'b0 && last_clock === 1'b1)
	  pipe_1[1] <= D;
    end // always @ (SCLK or rst_internal)
    
      
      
endmodule // IDDRX1F
