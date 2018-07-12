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
   ${comment} comp PLL
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name PLL;
   ${comment}       program "MODE:EHXPLLL "
   ${comment}               "EHXPLLL:::${settings}";
   ${comment}    }
   ${comment}    site ${loc};
   ${comment} }
}
