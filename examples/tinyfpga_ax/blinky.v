// Modified from:
// https://github.com/tinyfpga/TinyFPGA-A-Series/tree/master/template_a2

module TinyFPGA_A2 (
  inout pin1
);


  wire clk;

  OSCH #(
    .NOM_FREQ("2.08")
  ) internal_oscillator_inst (
    .STDBY(1'b0),
    .OSC(clk)
  );

  reg [23:0] led_timer;

  always @(posedge clk) begin
    led_timer <= led_timer + 1;
  end

  // left side of board
  assign pin1 = led_timer[23];
endmodule
