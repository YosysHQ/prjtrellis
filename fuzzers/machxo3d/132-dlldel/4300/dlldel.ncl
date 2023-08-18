::FROM-WRITER;
design top
{
   device
   {
      architecture se5c00;
      device LCMXO3D-4300HC;
      package CABGA256;
      performance "5";
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
