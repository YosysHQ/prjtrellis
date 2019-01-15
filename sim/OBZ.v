module OBZ(input I, T, output O);
    assign O = (T == 1) ? 1'bZ : I;
endmodule // OBZ
