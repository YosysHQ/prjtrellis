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
