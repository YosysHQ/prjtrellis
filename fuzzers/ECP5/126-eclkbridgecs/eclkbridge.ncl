::FROM-WRITER;
design top
{
   device
   {
      architecture sa5p00;
      device LFE5U-45F;
      package CABGA381;
      performance "8";
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
