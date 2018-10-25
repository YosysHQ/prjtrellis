module top(output osc);

OSCG #( .DIV(100) ) osc_i (.OSC(osc));

endmodule
