::FROM-WRITER;
design top
{
    device
    {
       architecture xo3c00f;
       device LCMXO3LF-1300E;
       package WLCSP36;
       performance "6";
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
      site "E3";
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
