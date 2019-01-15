module test_BB;
    wire B_sim, B_lat;
    wire O_sim, O_lat;
    reg  I, T;

    reg  b_q, b_tri;
    assign B_sim = b_tri ? 1'bz : b_q;
    assign B_lat = b_tri ? 1'bz : b_q;
    BB sim( .I(I),
	    .T(T),
	    .B(B_sim),
	    .O(O_sim));
    BB_l lat( .I(I),
	    .T(T),
	    .B(B_lat),
	    .O(O_lat));
    initial begin
	$dumpfile("BB.vcd");
	$dumpvars;

	b_tri = 1;
	b_q = 0;
	I = 0;
	T = 0;
	#10 I = 1;
	#10 T = 1;
	b_tri = 0;
	#10 b_q = 1;
	#10 I = 0;
	#20 $finish;
    end // UNMATCHED !!
endmodule // test_BB
