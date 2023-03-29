::FROM-WRITER;
design top
{
   device
   {
      architecture xo3c00f;
      device LCMXO3LF-6900C;
      package CABGA400;
      performance "6";
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
