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
