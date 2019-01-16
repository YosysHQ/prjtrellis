`timescale 1ns/1ps
module gsr_pur_assign(/*AUTOARG*/
    // Outputs
    GSR, PUR
    );
    output reg GSR, PUR;
    initial begin
	GSR = 0;
	PUR = 0;
	#10 GSR = 1;
	PUR = 1;
    end
endmodule // gsr_pur_assign

    
    
    
