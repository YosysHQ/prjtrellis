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
   ${comment} comp ES
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name ECLKSYNC;
   ${comment}       program "MODE:ECLKSYNCA "
   ${comment}               "ECLKSYNCA:#ON";
   ${comment}    }
   ${comment}    site ${site};
   ${comment} }


}
