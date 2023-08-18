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

   comp EBR
   {
      logical {
         cellmodel-name EBR;
         program "MODE:DP8KC "
                 "DP8KC:::GSR=DISABLED";
      }
      site EBR_R8C4;
   }

    signal q_c
   {
      signal-pins
         // drivers
         (EBR, DOA0),
         // loads
         (EBR, DIA0);
      ${route}
   }
}
