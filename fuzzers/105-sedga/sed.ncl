::FROM-WRITER;
design top
{
   device
   {
      architecture sa5p00;
      device LFE5U-45F;
      package CABGA381;
      performance "8";
   }
   ${comment} comp SED
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name SED;
   ${comment}       program "MODE:SEDGA "
   ${comment}               "SEDGA:::SED_CLK_FREQ=${clk_freq},CHECKALWAYS=${checkalways}";
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
