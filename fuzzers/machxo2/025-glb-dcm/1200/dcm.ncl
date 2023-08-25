::FROM-WRITER;
design top
{
   device
   {
       architecture xo2c00;
       device LCMXO2-1200HC;
       package QFN32;
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
