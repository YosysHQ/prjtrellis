::FROM-WRITER;
design top
{
   device
   {
      architecture xo3c00f;
      device LCMXO3LF-1300E;
      package CSFBGA121;
      performance "6";
   }
   ${comment} comp ES
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name ECLKBRIDGECS;
   ${comment}       program "MODE:ECLKBRIDGECS "
   ${comment}               "ECLKBRIDGECS:#ON";
   ${comment}    }
   ${comment}    site ${site};
   ${comment} }


}
