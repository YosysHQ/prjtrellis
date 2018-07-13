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
   ${comment} comp MULT
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name ALU54;
   ${comment}       program "MODE:${mode} "
   ${comment}               "${mode}:::${settings}";
   ${comment}    }
   ${comment}    site ${loc};
   ${comment} }
}
