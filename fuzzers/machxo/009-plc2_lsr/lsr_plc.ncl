::FROM-WRITER;
design top
{
    device
    {
      architecture mj5g00;
      device LCMXO2280C;
      package TQFP100;
      performance "3";
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
                 "CEMUX:CE "
                 "LSRMUX:${lsrmux} "
                 "SRMODE:${srmode} "
                 "M0MUX:M0 ";
         primitive REG0 q_6;
      }
      site R10C6${s};
   }

   comp lsr
   {
      logical
      {
         cellmodel-name PIO;
         program "PADDI:PADDI "
                 "IOBUF:::PULLMODE=DOWN ";
         primitive IOBUF lsr_pad;
         primitive PAD lsr;
      }
      site "13";
   }

   signal lsrc_c
   {
      signal-pins
         // drivers
         (lsr, PADDI),
         // loads
         (SLICE_0, LSR);
      route
         R10C6_LSR${l}.R10C6_LSR${l}_SLICE;
   }
}
