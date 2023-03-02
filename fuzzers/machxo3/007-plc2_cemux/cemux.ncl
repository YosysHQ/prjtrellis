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
      site R10C11${slice};
   }

}
