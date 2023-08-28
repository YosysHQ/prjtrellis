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
   ${comment} comp CDIV
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name CLKDIV;
   ${comment}       program "MODE:CLKDIVC "
   ${comment}               "CLKDIVC:::DIV=${div},GSR=${gsr}";
   ${comment}    }
   ${comment}    site ${site};
   ${comment} }


}
