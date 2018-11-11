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
   ${comment} comp CDIV
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name CLKDIV;
   ${comment}       program "MODE:CLKDIVF "
   ${comment}               "CLKDIVF:::DIV=${div},GSR=${gsr}";
   ${comment}    }
   ${comment}    site ${site};
   ${comment} }


}
