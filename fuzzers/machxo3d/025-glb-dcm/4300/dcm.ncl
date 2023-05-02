::FROM-WRITER;
design top
{
   device
   {
      architecture se5c00;
      device LCMXO3D-4300HC;
      package CABGA256;
      performance "5";
   }

  ${comment} comp I1
  ${comment} {
  ${comment}     logical
  ${comment}     {
  ${comment}        cellmodel-name DCM;
  ${comment}        program "MODE:DCMA "
  ${comment}                "DCMA:#ON ";
  ${comment}     }
  ${comment}     site ${site};
  ${comment}  }
}
