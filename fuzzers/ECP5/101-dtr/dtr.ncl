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
   ${comment} comp DTR_N
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name DTR;
   ${comment}       program "MODE:DTR "
   ${comment}               "DTR:#ON ";
   ${comment}    }
   ${comment}    site DTR;
   ${comment} }


}
