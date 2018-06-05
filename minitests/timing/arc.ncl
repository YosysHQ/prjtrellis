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
      site R6C10A;
   }

   comp SLICE_1
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
      site R6C40A;
   }


    signal q_c
   {
      signal-pins
         // drivers
         (SLICE_1, Q0),
         // loads
         (SLICE_0, A0);
      route
         R6C10_H02W0701.R6C10_A0;
   }
}
