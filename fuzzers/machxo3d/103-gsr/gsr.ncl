::FROM-WRITER;
design top
{
   device
   {
      architecture se5c00;
      device LCMXO3D-9400HC;
      package CABGA256;
      performance "5";
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
