module osch (
  input clk,
  output stdby
);

  wire out;

  OSCH #(
    .NOM_FREQ("2.08")
  ) osch_clk (
    .STDBY(stdby),
    .OSC(out)
  );

  assign clk = stdby;

endmodule
