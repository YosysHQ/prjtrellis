::FROM-WRITER;
design top
{
    device
    {
      architecture se5c00;
      device LCMXO3D-9400HC;
      package CABGA484;
      performance "5";
    }

   comp PIO
   {
      logical
      {
         cellmodel-name PIO;
         program "TRIMUX:PADDT:::PADDT=0 "
                 "IOBUF:::PULLMODE=NONE,DRIVE=8, \"
                    "SLEWRATE=SLOW,HYSTERESIS=NA "
                 "DATAMUX:PADDO "
                 "VREF:OFF "
                 "ODMUX:TRIMUX "
                 "LVDSMUX:DATAMUX ";
         primitive IOBUF PIO_pad;
         primitive PAD PIO;
      }
      site "T11";
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
