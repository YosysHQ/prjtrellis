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

   comp SLICE_0
      [,,,,A0,B0,D0,C0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,]
   {
      logical
      {
         cellmodel-name SLICE;
         program "MODE:LOGIC "
                 "K0::H0=0 "
                 "F0:F ";
         primitive K0 i3_4_lut;
      }
      site R2C2A;
   }

    signal q_c
   {
      signal-pins
         // drivers
         (SLICE_0, F0),
         // loads
         (SLICE_0, CLK);
      ${route}
   }
}
