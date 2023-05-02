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
   ${comment} comp JTAG
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name JTAG;
   ${comment}       program "MODE:JTAGF "
   ${comment}               "JTAGF:::ER1=${er1},ER2=${er2}";
   ${comment}    }
   ${comment}    site JTAG;
   ${comment} }


}
