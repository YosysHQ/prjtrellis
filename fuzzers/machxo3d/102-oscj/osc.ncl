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

   ${comment} comp OSC
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name OSC;
   ${comment}       program "${program}"
   ${using_non_default_freq} ${stdby} ${comment}               "OSCJ:#ON ";
   ${using_non_default_freq} ${stdby_0} ${comment}               "OSCJ::::STDBY=0 ";
   ${using_default_freq} ${comment}               "OSCJ:::NOM_FREQ=${nom_freq}:STDBY=0 ";
   ${comment}    }
   ${comment}    site OSC;
   ${comment} }
}
