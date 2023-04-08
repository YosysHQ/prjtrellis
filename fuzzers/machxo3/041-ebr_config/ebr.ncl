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
         program "MODE:${mode} "
                 "${mode}:::${settings}";
      }
      site EBR_${loc};
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
