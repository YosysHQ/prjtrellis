::FROM-WRITER;
design top
{
   device
   {
      architecture se5c00;
      device LCMXO3D-9400HC;
      package CABGA256;
      performance "6";
   }
   ${comment} comp efb
   ${comment} {
   ${comment}    logical {
   ${comment}       cellmodel-name EFB;
   ${comment}       program "MODE:EFBB "
   ${comment}               "EFBB:::EFB_SPI=ENABLED,EFB_TC_PORTMODE=WB,EFB_I2C2=ENABLED,EFB_TC=ENABLED, \"
   ${comment}                  "EFB_WB_CLK_FREQ=2.1,TC_TOP_SEL=OFF, \"
   ${comment}                  "TC_OVERFLOW=DISABLED:${efb}\"
   ${comment}                  "WBADRI5=0,WBADRI7=0,UFMSN=1,I2C1SCLI=0, \"
   ${comment}                  "I2C1SDAI=0,I2C2SDAI=0, \"
   ${comment}                  "TCRSTN=0,TCIC=0,PLL0DATI0=0, \"
   ${comment}                  "PLL0DATI1=0,PLL0DATI2=0,PLL0DATI3=0, \"
   ${comment}                  "PLL0DATI4=0,PLL0DATI5=0,PLL0DATI6=0, \"
   ${comment}                  "PLL0DATI7=0,PLL0ACKI=0,PLL1DATI0=0, \"
   ${comment}                  "PLL1DATI1=0,PLL1DATI2=0,PLL1DATI3=0, \"
   ${comment}                  "PLL1DATI4=0,PLL1DATI5=0,PLL1DATI6=0, \"
   ${comment}                  "PLL1DATI7=0,PLL1ACKI=0 ";
   ${comment}    }
   ${comment}    site EFB;
   ${comment} }


}
