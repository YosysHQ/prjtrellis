::FROM-WRITER;
design top
{
   device
   {
       architecture xo2c00;
       device LCMXO2-1200HC;
       package QFN32;
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
                 "CEMUX:1 "
                 "LSRMUX:LSR "
                 "SRMODE:LSR_OVER_CE "
                 "M0MUX:${m0mux} "
                 "M1MUX:${m1mux} ";
         primitive REG0 q_6;
      }
      site R10C11${slice};
   }

}
