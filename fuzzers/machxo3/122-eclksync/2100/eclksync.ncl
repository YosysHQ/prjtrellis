::FROM-WRITER;
design top
{
   device
   {
      architecture xo3c00f;
      device LCMXO3LF-2100C;
      package CABGA256;
      performance "6";
   }
   ${comment} comp ES
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name ECLKSYNC;
   ${comment}       program "MODE:ECLKSYNCA "
   ${comment}               "ECLKSYNCA:#ON";
   ${comment}    }
   ${comment}    site ${site};
   ${comment} }


}
