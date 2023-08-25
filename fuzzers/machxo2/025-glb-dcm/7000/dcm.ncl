::FROM-WRITER;
design top
{
   device
   {
        architecture xo2c00;
        device LCMXO2-7000HC;
        package FPBGA484;
        performance "6";
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
