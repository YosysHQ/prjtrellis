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
   ${comment} comp DCS
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name DCS;
   ${comment}       program "MODE:DCSC "
   ${comment}               "DCSC:::DCSMODE=${dcsmode}";
   ${comment}    }
   ${comment}    site ${site};
   ${comment} }


}
