::FROM-WRITER;
design top
{
   device
   {
       architecture xo3c00f;
       device LCMXO3LF-1300E;
       package WLCSP36;
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
