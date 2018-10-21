::FROM-WRITER;
design top
{
   device
   {
      architecture sa5p00;
      device LFE5U-25F;
      package CABGA381;
      performance "8";
   }

   ${comment} comp Q_MGIOL
   ${comment} {
   ${comment}   logical
   ${comment}   {
   ${comment}      cellmodel-name ${s}IOLOGIC;
   ${comment}      ${program};
   ${comment}   }
   ${comment}   site ${loc};
   ${comment} }
}
