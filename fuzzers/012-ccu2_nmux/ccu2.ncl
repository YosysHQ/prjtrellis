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

   comp SLICE_0
   {
      logical
      {
         cellmodel-name SLICE;
         program "MODE:CCU2 "
                 "CCU2::S0=0x9009,S1=0x9009${muxcfg}"
                 "FCO:FCO ";
         primitive CCU2 "CCU";
      }
      site R19C33${slice};
   }

}
