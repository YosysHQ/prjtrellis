::FROM-WRITER;
design top
{
   device
   {
        architecture xo2c00;
        device LCMXO2-7000HC;
        package FPBGA484;
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
