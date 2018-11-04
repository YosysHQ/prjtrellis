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
   ${comment} comp GSR
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name GSR;
   ${comment}       program "GSRMODE:${gsrmode} "
   ${comment}               "SYNCMODE:${syncmode}";
   ${comment}    }
   ${comment}    site GSR;
   ${comment} }


}
