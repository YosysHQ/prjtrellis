::FROM-WRITER;
design top
{
   device
   {
      architecture se5c00;
      device LCMXO3D-9400HC;
      package CABGA256;
      performance "5";
   }
   ${comment} comp ts
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name TSALL;
   ${comment}       program "MODE:TSALL "
   ${comment}               "TSALL:${tsall}";
   ${comment}    }
   ${comment}    site TSALL;
   ${comment} }


}
