::FROM-WRITER;
design top
{
   device
   {
       architecture xo2c00;
       device LCMXO2-1200HC;
       package QFN32;
       performance "6";
   }

   comp SLICE_0
   {
      logical
      {
         cellmodel-name SLICE;
         program "MODE:CCU2 "
                 "CCU2::S0=0xfaaa,S1=0xfaaa${muxcfg}"
                 "FCO:FCO ";
         primitive CCU2 "CCU";
      }
      site R10C11${slice};
   }

}
