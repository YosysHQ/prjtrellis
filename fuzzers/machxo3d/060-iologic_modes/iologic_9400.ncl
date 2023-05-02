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

   ${comment} comp io
   ${comment} {
   ${comment}   logical
   ${comment}   {
   ${comment}      cellmodel-name ${side}IOLOGIC;
   ${comment}      ${program};
   ${comment}   }
   ${comment}   site ${loc};
   ${comment} }
}
