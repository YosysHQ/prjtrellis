::FROM-WRITER;
design top
{
   device
   {
      architecture xo2c00;
      device LCMXO2-2000HC;
      package CABGA256;
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
