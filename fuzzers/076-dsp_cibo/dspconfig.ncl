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
   comp MULT
   {
      logical {
         cellmodel-name MULT18;
         program "MODE:MULT18X18D "
         "MULT18X18D:::REG_PIPELINE_CLK=NONE,REG_PIPELINE_RST=RST0,REG_OUTPUT_RST=RST0,\"
         "REG_INPUTA_RST=RST0,REG_INPUTB_RST=RST0,REG_INPUTA_RST=RST0,REG_INPUTB_RST=RST0,REG_INPUTA_CE=CE0,\"
         "REG_INPUTB_CE=CE0,REG_PIPELINE_CE=CE0,SOURCEB_MODE=B_SHIFT,REG_INPUTA_CLK=NONE,REG_INPUTB_CLK=NONE,\"
         "REG_INPUTC_CLK=NONE,REG_OUTPUT_CLK=${outclk}";
      }
      site ${loc};
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
         (MULT, P0),
         // loads
         (SLICE_0, A0);
      ${route}
   }


   signal a_c
   {
      signal-pins
         // drivers
         (SLICE_0, F0),
         // loads
         (MULT, A0);
      route
        ${rc}_JMULTA0.${rc}_JA0_MULT18,
        ${rc}_JMUIA0.${rc}_JMULTA0;
   }

}
