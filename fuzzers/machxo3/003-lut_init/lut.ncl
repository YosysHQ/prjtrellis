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
         program "MODE:LOGIC "
                 "K${k}::H${k}=${lut_func} "
                 "F${k}:F ";
         primitive K${k} i3_4_lut;
      }
      site R10C11${slice};
   }

}
