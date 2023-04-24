::FROM-WRITER;
design top
{
   device
   {
       architecture mj5g00;
       device LCMXO2280C;
       package TQFP100;
       performance "5";
   }

   comp SLICE_0
   {
      logical
      {
         cellmodel-name FSLICE;
         program "MODE:LOGIC "
                 "K${k}::H${k}=${lut_func} "
                 "F${k}:F ";
         primitive K${k} i3_4_lut;
      }
      site R2C2${slice};
   }

}
