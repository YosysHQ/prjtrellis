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
   ${comment} comp ts
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name TSALL;
   ${comment}       program "MODE:TSALL "
   ${comment}               "TSALL:${tsall}";
   ${comment}    }
   ${comment}    site TSALL;
   ${comment} }


}
