::FROM-WRITER;
design top
{
   device
   {
      architecture se5c00;
      device LCMXO3D-9400HC;
      package CABGA256;
      performance "5";
   }
   ${comment} comp SED
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name SED;
   ${comment}       program "MODE:SEDFA "
   ${comment}               "SEDFA:::SED_CLK_FREQ=${clk_freq},CHECKALWAYS=${checkalways}";
   ${comment}    }
   ${comment}    site SED;
   ${comment} }

   ${scomment}  signal q_c
   ${scomment} {
   ${scomment}    signal-pins
   ${scomment}       // drivers
   ${scomment}       (SED, AUTODONE),
   ${scomment}       // loads
   ${scomment}       (SED, SEDEXCLK);
   ${scomment} }

}
