::FROM-WRITER;
design top
{
   device
   {
      architecture xo2c00;
      device LCMXO2-1200HC;
      package TQFP144;
      performance "6";
   }
   ${comment} comp pcntr
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name PCNTR;
   ${comment}       program "MODE:PCNTR "
   ${comment}               "PCNTR:::${program}";
   ${comment}    }
   ${comment}    site PCNTR;
   ${comment} }


}
