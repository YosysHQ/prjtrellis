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
