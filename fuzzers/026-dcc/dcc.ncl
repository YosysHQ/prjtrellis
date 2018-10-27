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
   ${comment} comp DCC
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name DCC;
   ${comment}       program "MODE:DCCA "
   ${comment}               "DCCA::::CE=#SIG";
   ${comment}    }
   ${comment}    site ${site};
   ${comment} }


}
