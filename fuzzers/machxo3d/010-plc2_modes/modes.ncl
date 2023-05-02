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
         program "MODE:${mode} ";
         primitive REG0 q_6;
      }
      site R10C11${slice};
   }

}
