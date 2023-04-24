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
   {
      logical
      {
         cellmodel-name FSLICE;
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
      site R2C2${slice};
   }

}
