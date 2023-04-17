::FROM-WRITER;
design top
{
   device
   {
      architecture xo3c00f;
      device LCMXO3LF-1300E;
      package CSFBGA121;
      performance "6";
   }

    comp Q_MGIOL
    {
      logical
      {
         cellmodel-name ${s}IOLOGIC;
         program "GSR:${gsr} "
                 "MODE:IDDR_ODDR "
                 "CLKIMUX:${clkimux} "
                 "LSRIMUX:${lsrimux} "
                 "CLKOMUX:${clkomux} "
                 "LSROMUX:${lsromux} "
                 "LSRMUX:${lsrmux} "
                 "${ddr}";
      }
      site ${loc};
    }

    comp PIO
    {
      logical
      {
         cellmodel-name PIO;
         program "DATAMUX:${datamux}";
         primitive IOBUF Q_pad;
         primitive PAD Q;
      }
      site ${pin};
    }
}
