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
      site R6C11A;
   }

   comp SLICE_1
      [,,,,A0,B0,D0,C0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,]
   {
      logical
      {
         cellmodel-name SLICE;
         program "MODE:LOGIC "
                 "K1::H1=0 "
                 "F1:F ";
         primitive K1 i3_5_lut;
      }
      site R6C10C;
   }


    signal q_c
   {
      signal-pins
         // drivers
         (SLICE_1, F1),
         // loads
         (SLICE_0, A0);
      route
         R6C10_F5.R6C11_H01E0001;
   }
}
