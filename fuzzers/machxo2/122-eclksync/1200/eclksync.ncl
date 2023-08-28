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
