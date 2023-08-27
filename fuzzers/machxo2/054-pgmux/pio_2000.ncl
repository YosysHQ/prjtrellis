::FROM-WRITER;
design top
{
   device
   {
        architecture xo2c00;
        device LCMXO2-2000HC;
        package CABGA256;
        performance "6";
   }

    comp PIO
    {
      logical
      {
         cellmodel-name PIO;
         program "PADDI:PADDI "
                 "IOBUF:::PULLMODE=DOWN,CLAMP=ON "
                 "VREF:OFF "
                 "PGMUX:${pgmux} "
                 "PGBUF:#ON "
                 "INRDMUX:PGMUX ";
      }
      site ${loc};
    }
}
