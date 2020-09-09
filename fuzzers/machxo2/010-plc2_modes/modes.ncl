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
         program "MODE:${mode} ";
         primitive REG0 q_6;
      }
      site R10C11${slice};
   }

}
