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
         program "MODE:DPRAM "
                 "DPRAM::DO0=0x0000,DO1=0x0000 "
                 "WREMUX:${wremux} ";
         primitive DPRAM q_6;
      }
      site R10C11${slice};
   }

}
