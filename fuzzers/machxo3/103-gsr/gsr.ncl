::FROM-WRITER;
design top
{
   device
   {
      architecture xo3c00f;
      device LCMXO3LF-1300E;
      package WLCSP36;
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
