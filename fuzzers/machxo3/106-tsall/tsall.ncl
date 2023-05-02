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
