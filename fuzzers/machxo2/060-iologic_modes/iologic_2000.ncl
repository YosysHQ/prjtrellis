::FROM-WRITER;
design top
{
   device
   {
      architecture xo2c00;
      device LCMXO2-2000HC;
      package CABGA256;
      performance "6";
   }

   ${comment} comp io
   ${comment} {
   ${comment}   logical
   ${comment}   {
   ${comment}      cellmodel-name ${side}IOLOGIC;
   ${comment}      ${program};
   ${comment}   }
   ${comment}   site "${loc}";
   ${comment} }
}
