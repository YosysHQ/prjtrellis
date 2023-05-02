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
