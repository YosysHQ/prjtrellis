::FROM-WRITER;
design top
{
    device
    {
        architecture xo3c00f;
        device LCMXO3LF-9400C;
        package CABGA484;
        performance "6";
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
                 "CLKMUX:${clkmode} "
                 "CEMUX:1 "
                 "LSRMUX:LSR "
                 "SRMODE:LSR_OVER_CE "
                 "M0MUX:M0 ";
         primitive REG${r} q_6;
      }
      site R10C11${slice};
   }

}
