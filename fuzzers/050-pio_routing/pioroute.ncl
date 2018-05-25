::FROM-WRITER;
design top
{
   device
   {
      architecture sa5p00;
      device LFE5U-45F;
      package CABGA381;
      performance "8";
   }

   comp PIO
   {
      logical
      {
         cellmodel-name PIO;
         program "TRIMUX:PADDT:::PADDT=0 "
                 "IOBUF:::PULLMODE=NONE,DRIVE=8, \"
                    "SLEWRATE=SLOW,CLAMP=ON,HYSTERESIS=NA "
                 "DATAMUX:PADDO "
                 "VREF:OFF "
                 "ODMUX:TRIMUX "
                 "LVDSMUX:DATAMUX ";
         primitive IOBUF PIO_pad;
         primitive PAD PIO;
      }
      site T3;
   }

    signal q_c
   {
      signal-pins
         // drivers
         (PIO, PADDI),
         // loads
         (PIO, PADDO);
      ${route}
   }
}
