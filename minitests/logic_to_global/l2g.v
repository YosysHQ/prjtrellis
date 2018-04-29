module global_test(input a, input b, output q);

wire clk = a&b /* synthesis COMP=slicex LOC="R45C2A" */;


reg reg_0 /* synthesis COMP=slice0 LOC="R2C2D" */;
reg reg_1 /* synthesis COMP=slice1 LOC="R2C124D" */;
reg reg_2 /* synthesis COMP=slice2 LOC="R93C124A" */;
reg reg_3 /* synthesis COMP=slice3 LOC="R93C2A" */;
reg reg_4;

always @(posedge clk) begin
	reg_0 <= a;
	reg_1 <= reg_0;
	reg_2 <= reg_1;
	reg_3 <= reg_2;
	reg_4 <= reg_3;
end

assign q = reg_4;

endmodule
