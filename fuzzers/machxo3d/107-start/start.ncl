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
