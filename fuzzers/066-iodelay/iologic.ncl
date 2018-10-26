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


    comp Q_MGIOL
    {
      logical
      {
         cellmodel-name ${s}IOLOGIC;
         program "${delay}"
                 "${program}";
      }
      site ${loc};
    }

   signal q_c
   {
      signal-pins
         // drivers
         (SLICE_0, F0),
         // loads
         (SLICE_0, A0);
      ${route}
   }
}
