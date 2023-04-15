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
   ${comment} comp start
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name START;
   ${comment}       program "MODE:START "
   ${comment}               "START:${start}";
   ${comment}    }
   ${comment}    site START;
   ${comment} }


}
