::FROM-WRITER;
design top
{
   device
   {
      architecture xo3c00f;
      device LCMXO3LF-1300E;
      package WLCSP36;
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
