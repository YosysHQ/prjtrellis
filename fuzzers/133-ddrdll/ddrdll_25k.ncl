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
   ${comment} comp DDRDLL0
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name DDRDLL;
   ${comment}       program "MODE:DDRDLLA "
   ${comment}               "DDRDLLA:::${program}";
   ${comment}    }
   ${comment}    site ${site};
   ${comment} }


}
