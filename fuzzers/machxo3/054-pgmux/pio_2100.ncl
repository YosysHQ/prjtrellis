::FROM-WRITER;
design top
{
   device
   {
      architecture xo3c00f;
      device LCMXO3LF-2100C;
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
