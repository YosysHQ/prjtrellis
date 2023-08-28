::FROM-WRITER;
design top
{
   device
   {
      architecture xo2c00;
      device LCMXO2-1200HC;
      package TQFP144;
      performance "6";
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
