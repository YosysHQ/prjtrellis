::FROM-WRITER;
design top
{
   device
   {
      architecture sa5p00;
      device LFE5U-25F;
      package CABGA381;
      performance "8";
   }

    comp Q_MGIOL
    {
      logical
      {
         cellmodel-name IOLOGIC;
         program "MODE:IDDRXN "
                 "IDDRXN:::DDRMODE=${mode}";
      }
      site ${loc};
    }
}
