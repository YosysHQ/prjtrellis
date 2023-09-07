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
