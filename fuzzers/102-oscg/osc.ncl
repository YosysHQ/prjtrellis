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
   ${comment} comp OSC
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name OSC;
   ${comment}       program "MODE:OSCG "
   ${comment}               "OSCG:::DIV=${div}";
   ${comment}    }
   ${comment}    site OSC;
   ${comment} }


}
