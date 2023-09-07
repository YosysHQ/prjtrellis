::FROM-WRITER;
design top
{
   device
   {
        architecture xo2c00;
        device LCMXO2-1200HC;
        package QFN32;
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
