::FROM-WRITER;
design top
{
   device
   {
      architecture se5c00;
      device LCMXO3D-4300HC;
      package CABGA256;
      performance "5";
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
