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

    comp Q_MGIOL
    {
      logical
      {
         cellmodel-name ${s}IOLOGIC;
         program "GSR:ENABLED "
                 "MODE:IREG_OREG "
                 "CEIMUX:${ceimux} "
                 "SRMODE:${srmode} "
                 "CEOMUX:${ceomux} "
                 "CLKIMUX:${clkimux} "
                 "LSRIMUX:LSRMUX "
                 "CLKOMUX:${clkomux} "
                 "LSROMUX:LSRMUX "
                 "LSRMUX:LSR "
                 "${reg}";
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
