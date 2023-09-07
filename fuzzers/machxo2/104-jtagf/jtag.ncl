::FROM-WRITER;
design top
{
   device
   {
      architecture xo2c00;
      device LCMXO2-2000HC;
      package CABGA256;
      performance "6";
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
