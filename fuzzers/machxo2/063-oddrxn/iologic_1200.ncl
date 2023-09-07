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
         cellmodel-name TIOLOGIC;
         program "MODE:ODDR4 "
                 "${mode}";
      }
      site "${loc}";
    }
}
