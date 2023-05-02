::FROM-WRITER;
design top
{
   device
   {
      architecture xo3c00f;
      device LCMXO3LF-2100C;
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
