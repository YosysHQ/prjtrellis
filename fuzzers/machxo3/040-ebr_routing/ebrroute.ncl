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

   comp EBR
   {
      logical {
         cellmodel-name EBR;
         program "MODE:DP8KC "
                 "DP8KC:::GSR=DISABLED";
      }
      site EBR_R6C17;
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
