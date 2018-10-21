::FROM-WRITER;
design top
{
   device
   {
      architecture sa5p00g;
      device LFE5UM5G-45F;
      package CABGA381;
      performance "8";
   }

   comp DCU
   {
      logical {
         cellmodel-name DCU;
         program "MODE:DCUA ";
      }
      site DCU0;
   }

    signal q_c
   {
      signal-pins
         // drivers
         (DCU, CH0_FF_RX_D_0),
         // loads
         (DCU, CH0_FF_TX_D_0);
      ${route}
   }
}
