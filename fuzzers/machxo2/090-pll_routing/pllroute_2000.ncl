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

   comp PLL
   {
      logical {
         cellmodel-name PLL;
         program "MODE:EHXPLLJ ";
      }
      site LPLL;
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
