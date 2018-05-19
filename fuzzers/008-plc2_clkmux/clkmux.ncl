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
                 "CLKMUX:${clkmux} "
                 "CEMUX:CE "
                 "LSRMUX:LSR "
                 "SRMODE:LSR_OVER_CE "
                 "M0MUX:M0 ";
         primitive REG0 q_6;
      }
      site R19C33A;
   }

      comp clk
   {
      logical
      {
         cellmodel-name PIO;
         program "PADDI:PADDI "
                 "IOBUF:::CLAMP=ON "
                 "VREF:OFF "
                 "INRDMUX:INBUF "
                 "MIPIMUX:INRDMUX ";
         primitive IOBUF clk_pad;
         primitive PAD clk;
      }
      site B11;
   }

   signal clk_c
   {
      signal-pins
         // drivers
         (clk, PADDI),
         // loads
         (SLICE_0, CLK);
      route
         R19C33_CLK${c}.R19C33_MUXCLK0,
         R19C33_MUXCLK0.R19C33_CLK0_SLICE;
   }
}
