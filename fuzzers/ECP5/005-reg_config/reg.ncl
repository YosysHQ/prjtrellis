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
   {
      logical
      {
         cellmodel-name SLICE;
         program "MODE:LOGIC "
                 "REG${r}:::REGSET=${regset},LSRMODE=${lsrmode}:SD=${sd} "
                 "Q${r}:Q "
                 "GSR:${gsr} "
                 "CLKMUX:CLK "
                 "CEMUX:1 "
                 "LSRMUX:LSR "
                 "SRMODE:LSR_OVER_CE "
                 "M0MUX:M0 ";
         primitive REG${r} q_6;
      }
      site R19C33${slice};
   }

}
