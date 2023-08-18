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
