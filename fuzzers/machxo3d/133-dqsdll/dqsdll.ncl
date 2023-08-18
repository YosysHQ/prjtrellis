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
   ${comment} comp DDRDLL0
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name DQSDLL;
   ${comment}       program "MODE:DQSDLLC "
   ${comment}               "DQSDLLC:::${program}";
   ${comment}    }
   ${comment}    site ${site};
   ${comment} }


}
