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
   ${comment} comp PLL
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name PLL;
   ${comment}       program "MODE:EHXPLLJ "
   ${comment}               "EHXPLLJ:::${settings}";
   ${comment}    }
   ${comment}    site ${loc};
   ${comment} }
}
