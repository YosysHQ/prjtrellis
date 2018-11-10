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

   ${comment} comp DCU
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name DCU;
   ${comment}       program "MODE:DCUA "
   ${comment}               "DCUA:::${settings}";
   ${comment}    }
   ${comment}    site DCU0;
   ${comment} }
}
