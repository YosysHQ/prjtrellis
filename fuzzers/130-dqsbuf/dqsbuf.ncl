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
   ${comment} comp DQS0
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name DQS;
   ${comment}       program "MODE:DQSBUFM "
   ${comment}               "DQSBUFM:::${program}";
   ${comment}    }
   ${comment}    site ${site};
   ${comment} }


}
