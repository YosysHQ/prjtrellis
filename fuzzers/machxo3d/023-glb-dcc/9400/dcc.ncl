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

  ${comment} comp I1
  ${comment} {
  ${comment}     logical
  ${comment}     {
  ${comment}        cellmodel-name DCC;
  ${comment}        program "MODE:DCCA "
  ${comment}                "DCCA:#ON ";
  ${comment}     }
  ${comment}     site ${site};
  ${comment}  }
}
