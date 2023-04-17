::FROM-WRITER;
design top
{
   device
   {
      architecture xo3c00f;
      device LCMXO3LF-1300E;
      package CSFBGA121;
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
      site ${loc};
    }
}
