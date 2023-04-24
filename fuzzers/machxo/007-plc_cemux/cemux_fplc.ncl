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

   comp SLICE_0
   {
      logical
      {
         cellmodel-name FSLICE;
         program "MODE:LOGIC "
                 "REG0:::REGSET=RESET:SD=0 "
                 "Q0:Q "
                 "GSR:DISABLED "
                 "CLKMUX:CLK "
                 "CEMUX:${cemux} "
                 "LSRMUX:LSR "
                 "SRMODE:LSR_OVER_CE "
                 "M0MUX:M0 ";
         primitive REG0 q_6;
      }
      site R2C2${slice};
   }

}
