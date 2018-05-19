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
                 "CCU2::S0=0x9009,S1=0x9009:INJECT1_0=${ij1_0}, \"
                    "INJECT1_1=${ij1_1} "
                 "FCO:FCO ";
         primitive CCU2 "CCU";
      }
      site R19C33${slice};
   }

}
