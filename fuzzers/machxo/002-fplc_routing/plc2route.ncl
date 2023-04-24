::FROM-WRITER;
design top
{
    device
    {
       architecture mj5g00;
       device LCMXO2280C;
       package TQFP100;
       performance "5";
    }

   comp FSLICE_0
      [,,,,A0,B0,D0,C0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,]
   {
      logical
      {
         cellmodel-name FSLICE;
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
         (FSLICE_0, F0),
         // loads
         (FSLICE_0, A0);
      ${route}
   }
}
