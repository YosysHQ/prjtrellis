::FROM-WRITER;
design top
{
   device
   {
      architecture xo3c00f;
      device LCMXO3LF-1300E;
      package CSFBGA121;
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
