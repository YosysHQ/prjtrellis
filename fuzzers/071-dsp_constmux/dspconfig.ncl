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
    comp MULT
    {
       logical {
          cellmodel-name ${cmodel};
          program "MODE:${mode}"
                  "${mode}::::${settings}";
       }
       site ${loc};
    }
}
