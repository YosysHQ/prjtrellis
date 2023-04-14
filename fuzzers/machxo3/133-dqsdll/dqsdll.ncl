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
