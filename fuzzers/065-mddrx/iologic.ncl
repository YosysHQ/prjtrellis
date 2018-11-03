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
         cellmodel-name IOLOGIC;
         program "MODE:MIDDRX_MODDRX "
                 "${program}"
                 "IOLTOMUX:${ioltomux}";
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
