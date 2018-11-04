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
   ${comment} comp EXTREF
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name EXTREF;
   ${comment}       program "MODE:EXTREFB "
   ${comment}               "EXTREFB${program}";
   ${comment}    }
   ${comment}    site EXTREF0;
   ${comment} }


}
