module BB(/*AUTOARG*/
    // Outputs
    O,
    // Inouts
    B,
    // Inputs
    I, T
    );
    input I, T;
    output O;
    inout  B;

    assign B = (T == 1'b1) ? 1'bZ : I;

    assign O = B;
endmodule // BB
