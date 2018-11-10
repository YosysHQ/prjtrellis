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
      site R19C33A;
   }

   comp lsr
   {
      logical
      {
         cellmodel-name PIO;
         program "PADDI:PADDI "
                 "IOBUF:::CLAMP=ON "
                 "VREF:OFF "
                 "INRDMUX:INBUF "
                 "MIPIMUX:INRDMUX ";
         primitive IOBUF lsr_pad;
         primitive PAD lsr;
      }
      site B11;
   }

   signal lsrc_c
   {
      signal-pins
         // drivers
         (lsr, PADDI),
         // loads
         (SLICE_0, LSR);
      route
         R19C33_LSR${l}.R19C33_MUXLSR0,
         R19C33_MUXLSR0.R19C33_LSR0_SLICE;
   }
}
