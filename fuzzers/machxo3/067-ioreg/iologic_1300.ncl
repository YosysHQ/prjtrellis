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
         program "GSR:ENABLED "
                 "MODE:IREG_OREG "
                 "CEMUX:${cemux} "
                 "CEIMUX:${ceimux} "
                 "SRMODE:${srmode} "
                 "CEOMUX:${ceomux} "
                 "CLKIMUX:${clkimux} "
                 "LSRIMUX:LSRMUX "
                 "CLKOMUX:${clkomux} "
                 "LSROMUX:LSRMUX "
                 "LSRMUX:LSR "
                 "TSMUX:${tsmux} "
                 "${reg}";
      }
      site ${loc};
    }

    comp PIO
    {
      logical
      {
         cellmodel-name PIO;
         program "DATAMUX:${datamux} "
                 "TRIMUX:${trimux}";
         primitive IOBUF Q_pad;
         primitive PAD Q;
      }
      site ${pin};
    }
}
