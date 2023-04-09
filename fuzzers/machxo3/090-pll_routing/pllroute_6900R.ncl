::FROM-WRITER;
design top
{
   device
   {
      architecture xo3c00f;
      device LCMXO3LF-6900C;
      package CABGA400;
      performance "6";
   }

   comp PLL
   {
      logical {
         cellmodel-name PLL;
         program "MODE:EHXPLLJ ";
      }
      site RPLL;
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
