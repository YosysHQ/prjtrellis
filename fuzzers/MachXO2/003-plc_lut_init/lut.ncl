::FROM-WRITER;
design top
{
   device
   {
       architecture xo2c00;
       device LCMXO2-4000HC;
       package TQFP144;
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
      site R9C9${slice};
   }

}
