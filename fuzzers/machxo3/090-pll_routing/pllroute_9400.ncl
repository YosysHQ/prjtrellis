::FROM-WRITER;
design top
{
   device
   {
      architecture xo3c00f;
      device LCMXO3LF-9400C;
      package CABGA484;
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
