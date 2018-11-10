::FROM-WRITER;
design top
{
   device
   {
      architecture sa5p00;
      device LFE5U-45F;
      package CABGA381;
      performance "8";
   }
   ${comment} comp I_N
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name CCLK;
   ${comment}       program ;
   ${comment}       primitive PAD I_N;
   ${comment}    }
   ${comment}    site CCLK;
   ${comment} }


}
