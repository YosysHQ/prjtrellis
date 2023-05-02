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

    comp Q_MGIOL
    {
      logical
      {
         cellmodel-name BIOLOGIC;
         program "MODE:IDDR4 "
                 "${mode}";
      }
      site ${loc};
    }
}
