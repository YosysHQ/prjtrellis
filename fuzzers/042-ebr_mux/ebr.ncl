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
