::FROM-WRITER;
design top
{
   device
   {
       architecture xo3c00f;
       device LCMXO3LF-6900C;
       package CABGA400;
       performance "6";
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
