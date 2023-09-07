::FROM-WRITER;
design top
{
   device
   {
        architecture xo2c00;
        device LCMXO2-7000HC;
        package FPBGA484;
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
