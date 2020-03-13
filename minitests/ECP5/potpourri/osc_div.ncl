::FROM-WRITER;
// designname: top
// Creation time stamp: 10/24/18  20:04:40
design top
{
   device
   {
      architecture sa5p00;
      device LFE5U-45F;
      package CABGA381;
      performance "8";
   }


   comp osc_i
   {

      logical
      {
         cellmodel-name OSC;
         program "MODE:OSCG "
                 "OSCG:::DIV=64 ";
      }
      site OSC;
   }


}
