::FROM-WRITER;
design top
{
   device
   {
      architecture sa5p00;
      device LFE5U-25F;
      package CABGA381;
      performance "8";
   }
   ${comment} comp MULT
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name MULT18;
   ${comment}       program "MODE:${mode} "
   ${comment}               "${mode}:::${settings}:CLK0=#SIG,CLK1=#SIG,CLK2=#SIG,CLK3=#SIG,CE0=#INV,CE1=#INV,CE2=#INV,CE3=#INV,RST0=#INV,RST1=#INV,RST2=#INV,RST3=#INV";
   ${comment}    }
   ${comment}    site ${loc};
   ${comment} }
}
