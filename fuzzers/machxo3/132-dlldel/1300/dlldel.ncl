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
   ${comment} comp DLLDEL0
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name DLLDEL;
   ${comment}       program "MODE:DLLDELC "
   ${comment}               "DLLDELC:::${program}";
   ${comment}    }
   ${comment}    site ${site};
   ${comment} }


}
