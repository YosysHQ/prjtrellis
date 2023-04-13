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
   ${comment} comp SED
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name SED;
   ${comment}       program "MODE:${mode} "
   ${comment}               "${mode}:::";
   ${comment}    }
   ${comment}    site SED;
   ${comment} }
}
