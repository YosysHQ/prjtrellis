::FROM-WRITER;
design top
{
   device
   {
      architecture xo2c00;
      device LCMXO2-1200HC;
      package TQFP144;
      performance "6";
   }

    comp Q_MGIOL
    {
      logical
      {
         cellmodel-name BIOLOGIC;
         program "MODE:IDDR4 "
                 "${mode}";
      }
      site "${loc}";
    }
}
