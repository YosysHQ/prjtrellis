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
