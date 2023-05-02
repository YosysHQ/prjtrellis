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
