module top(input a, input b, input c, input d, input e, input f, input g, input clk, output q);

// https://www.guidgenerator.com/online-guid-generator.aspx
LUT7 #(.init (128'hd13686b35db74bd88bbb244fc3fd36af)) I1 ( .A (a), .B (b), .C (c), .D (d), .E (e), .F (f), .G (g),  .Z (q) );

endmodule
