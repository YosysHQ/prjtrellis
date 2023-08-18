::FROM-WRITER;
design top
{
   device
   {
      architecture se5c00;
      device LCMXO3D-9400HC;
      package CABGA256;
      performance "5";
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
