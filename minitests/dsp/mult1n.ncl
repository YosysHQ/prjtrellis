::FROM-WRITER;
// designname: dut
// Creation time stamp: 02/09/19  17:09:09
design dut
{
   device
   {
      architecture sa5p00;
      device LFE5U-25F;
      package CABGA381;
      performance "8";
   }

   comp dsp
   {

      logical
      {
         cellmodel-name MULT18;
         program "MODE:MULT18X18D "
                 "MULT18X18D:::";
      }
      site MULT18_R13C5;
   }
  
}
