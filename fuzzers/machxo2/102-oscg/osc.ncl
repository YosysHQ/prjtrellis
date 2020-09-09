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

   ${comment} comp OSC
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name OSC;
   ${comment}       program "${program}"
   ${using_non_default_freq} ${stdby} ${comment}               "OSCH:#ON ";
   ${using_non_default_freq} ${stdby_0} ${comment}               "OSCH::::STDBY=0 ";
   ${using_default_freq} ${comment}               "OSCH:::NOM_FREQ=${nom_freq}:STDBY=0 ";
   ${comment}    }
   ${comment}    site OSC;
   ${comment} }
}
