::FROM-WRITER;
design top
{
   device
   {
      architecture sa5p00;
      device LFE5U-45F;
      package CABGA381;
      performance "8";
   }
   ${comment} comp JTAG
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name JTAG;
   ${comment}       program "MODE:JTAGG "
   ${comment}               "JTAGG:::ER1=${er1},ER2=${er2}";
   ${comment}    }
   ${comment}    site JTAG;
   ${comment} }


}
