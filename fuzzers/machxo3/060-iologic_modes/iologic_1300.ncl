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
