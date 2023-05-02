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
         program "MODE:${mode} ";
         primitive REG0 q_6;
      }
      site R10C11${slice};
   }

}
