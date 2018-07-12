::FROM-WRITER;
design top
{
   device
   {
      architecture sa5p00;
      device LFE5U-45F;
      package CABGA381;
      performance "8";
   }

   comp PLL
   {
      logical {
         cellmodel-name PLL;
         program "MODE:EHXPLLL ";
      }
      site PLL_TL0;
   }

    signal q_c
   {
      signal-pins
         // drivers
         (PLL, LOCK),
         // loads
         (PLL, RST);
      ${route}
   }
}
