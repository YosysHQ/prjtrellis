`timescale 1ns/1ps
module ODDRX2F(/*AUTOARG*/
    // Outputs
    Q,
    // Inputs
    D0, D1, D2, D3, RST, ECLK, SCLK
    );
    input D0, D1, D2, D3;
    input RST;
    input ECLK, SCLK;
    output reg Q;

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

    reg [3:0] pipe_1;
    reg [3:0] pipe_2;
    reg [3:0] pipe_3;
    reg [1:0] out_next;

    always @(posedge SCLK or posedge rst_internal)
	if(rst_internal == 1'b1) begin
	    pipe_1 <= 4'h0;
	    pipe_2 <= 4'h0;
	    pipe_3 <= 4'h0;
	end
	else begin
	  pipe_1 <= {D3, D2, D1, D0};
	    pipe_2 <= pipe_1;
	    pipe_3 <= pipe_2;
	end
    

    always @(SCLK or posedge rst_internal)
	if(rst_internal == 1'b1) 
	    out_next <= 4'h0;
	else if(SCLK === 1)
	  out_next <= pipe_2[1:0];
	else 
	  out_next <= pipe_3[3:2];
    always @(ECLK or posedge rst_internal)
      if(rst_internal == 1'b1)
	Q <= 1'b0;
      else if(ECLK === 1)
	Q <= out_next[0];
      else if(ECLK === 0)
	Q <= out_next[1];
    

      
endmodule // ODDRX2F
