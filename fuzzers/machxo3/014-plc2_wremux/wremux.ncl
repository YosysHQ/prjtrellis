::FROM-WRITER;
design top
{
   device
   {
       architecture xo3c00f;
       device LCMXO3LF-1300E;
       package WLCSP36;
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
