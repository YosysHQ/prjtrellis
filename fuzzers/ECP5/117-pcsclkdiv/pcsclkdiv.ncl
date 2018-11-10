::FROM-WRITER;
design top
{
   device
   {
      architecture sa5p00g;
      device LFE5UM5G-45F;
      package CABGA381;
      performance "8";
   }
   ${comment} comp PCSCLKDIV
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name PCSCLKDIV;
   ${comment}       program "MODE:PCSCLKDIV "
   ${comment}               "PCSCLKDIV${program}";
   ${comment}    }
   ${comment}    site ${loc};
   ${comment} }


}
