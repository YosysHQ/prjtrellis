::FROM-WRITER;
design top
{
   device
   {
      architecture xo3c00f;
      device LCMXO3LF-6900C;
      package CABGA400;
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
