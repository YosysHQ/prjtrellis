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

   comp EBR
   {
      logical {
         cellmodel-name EBR;
         program "MODE:DP16KD "
                 "DP16KD:::GSR=DISABLED:\"
                 "${sig}=${val}";
      }
      site EBR_R25C26;
   }
}
