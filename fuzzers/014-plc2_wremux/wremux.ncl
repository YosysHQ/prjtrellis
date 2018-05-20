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
         program "MODE:DPRAM "
                 "DPRAM::DO0=0x0000,DO1=0x0000 "
                 "WREMUX:${wremux} ";
         primitive DPRAM q_6;
      }
      site R19C33${slice};
   }

}
