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
         program "GSR:${gsr} "
                 "MODE:IDDRX1_ODDRX1 "
                 "CLKIMUX:${clkimux} "
                 "LSRIMUX:${lsrimux} "
                 "CLKOMUX:${clkomux} "
                 "LSROMUX:${lsromux} "
                 "LSRMUX:${lsrmux} "
                 "${ddr}";
      }
      site ${loc};
    }
}
