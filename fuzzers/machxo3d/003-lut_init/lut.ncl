::FROM-WRITER;
design top
{
   device
   {
      architecture se5c00;
      device LCMXO3D-9400HC;
      package CABGA256;
      performance "5";
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
