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
