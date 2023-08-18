::FROM-WRITER;
design top
{
    device
    {
      architecture se5c00;
      device LCMXO3D-9400HC;
      package CABGA256;
      performance "5";
    }

   comp SLICE_0
   {
      logical
      {
         cellmodel-name SLICE;
         program "MODE:LOGIC "
                 "REG${r}:::REGSET=${regset}:SD=${sd} "
                 "Q${r}:Q "
                 "GSR:${gsr} "
                 "REGMODE:${regmode} "
                 "LSRMUX:LSR "
                 "SRMODE:LSR_OVER_CE "
                 "M0MUX:M0 ";
         primitive REG${r} q_6;
      }
      site R10C11${slice};
   }

}
