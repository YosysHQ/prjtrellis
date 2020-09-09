::FROM-WRITER;
// designname: top
// Creation time stamp: 01/31/20  05:21:54
design top
{
   device
   {
      architecture xo2c00;
      device LCMXO2-1200HC;
      package QFN32;
      performance "6";
   }

   // Writing 12 properties.
   property
   {
      LSE_CPS_MAP_FILE string "xxx_lse_sign_file";
      "PINNAME:0" string "clk";
      "PINNAME:1" string "d";
      "PINNAME:2" string "r";
      "PINNAME:3" string "s";
      "PINNAME:4" string "q";
      "PINTYPE:0" string "IN";
      "PINTYPE:1" string "IN";
      "PINTYPE:2" string "IN";
      "PINTYPE:3" string "IN";
      "PINTYPE:4" string "OUT";
      "SIGNAME:PUR" string "VCC_net";
   } // End of property list.

   // The Design macro definitions.
   // The Design macro instances.
   // The Design Comps.
   comp SLICE_0
   {

      // Writing 2 properties.
      property
      {
         LSE_CPS_ID_1 string "REG0";
         NGID0 long 2;
      } // End of property list.

      logical
      {
         cellmodel-name SLICE;
         program "MODE:LOGIC "
                 "REG0:::REGSET=SET:SD=0 "
                 "Q0:Q "
                 "GSR:ENABLED "
                 "CLKMUX:${clkmux} "
                 "CEMUX:1:::1=0 "
                 "LSRMUX:LSR "
                 "SRMODE:LSR_OVER_CE "
                 "LSRONMUX:LSRMUX "
                 "M0MUX:M0 "
                 "REGMODE:FF ";
         primitive REG0 ff;
      }
      site R10C6${c};
   }
   comp d
   {

      // Writing 3 properties.
      property
      {
         "#%PAD%PINID" long 1;
         LSE_CPS_ID_2 string "IOBUF";
         NGID0 long 3;
      } // End of property list.

      logical
      {
         cellmodel-name PIO;
         program "PADDI:PADDI "
                 "IOBUF:::PULLMODE=DOWN,CLAMP=ON "
                 "VREF:OFF "
                 "PGMUX:INBUF "
                 "INRDMUX:PGMUX ";
         primitive IOBUF d_pad;
         primitive PAD d;
      }
      site "10";
   }
   comp q
   {

      // Writing 3 properties.
      property
      {
         "#%PAD%PINID" long 4;
         LSE_CPS_ID_3 string "IOBUF";
         NGID0 long 4;
      } // End of property list.

      logical
      {
         cellmodel-name PIO;
         program "TRIMUX:PADDT:::PADDT=0 "
                 "IOBUF:::PULLMODE=DOWN,DRIVE=8, \"
                    "SLEWRATE=SLOW,HYSTERESIS=NA "
                 "DATAMUX:PADDO "
                 "VREF:OFF "
                 "ODMUX:TRIMUX "
                 "LVDSMUX:DATAMUX ";
         primitive IOBUF q_pad;
         primitive PAD q;
      }
      site "9";
   }
   comp r
   {

      // Writing 3 properties.
      property
      {
         "#%PAD%PINID" long 2;
         LSE_CPS_ID_5 string "IOBUF";
         NGID0 long 6;
      } // End of property list.

      logical
      {
         cellmodel-name PIO;
         program "PADDI:PADDI "
                 "IOBUF:::PULLMODE=DOWN,CLAMP=ON "
                 "VREF:OFF "
                 "PGMUX:INBUF "
                 "INRDMUX:PGMUX ";
         primitive IOBUF r_pad;
         primitive PAD r;
      }
      site "28";
   }
   comp s
   {

      // Writing 3 properties.
      property
      {
         "#%PAD%PINID" long 3;
         LSE_CPS_ID_6 string "IOBUF";
         NGID0 long 7;
      } // End of property list.

      logical
      {
         cellmodel-name PIO;
         program "PADDI:PADDI "
                 "IOBUF:::PULLMODE=DOWN,CLAMP=ON "
                 "VREF:OFF "
                 "PGMUX:INBUF "
                 "INRDMUX:PGMUX ";
         primitive IOBUF s_pad;
         primitive PAD s;
      }
      site "8";
   }
   comp GSR_INST
   {

      // Writing 2 properties.
      property
      {
         LSE_CPS_ID_4 string "GSR";
         NGID0 long 5;
      } // End of property list.

      logical
      {
         cellmodel-name GSR;
         program "GSRMODE:ACTIVE_LOW "
                 "SYNCMODE:ASYNC ";
      }
      site GSR;
   }
   // The Design Signals.
   signal d_c
   {
      signal-pins
         // drivers
         (d, PADDI),
         // loads
         (SLICE_0, M0);
      route
         R10C6_H00L0200.R10C6_M0,
         R10C6_V02N0301.R10C6_H00L0200,
         R11C6_JQ3.R10C6_V02N0301,
         R12C6_JDID.R11C6_JQ3,
         R10C6_M0.R10C6_M0_SLICE,
         R12C6_JPADDID_PIO.R12C6_JDID;
   }
   signal s_c
   {
      signal-pins
         // drivers
         (s, PADDI),
         // loads
         (SLICE_0, LSR);
      route
         R10C6_V00T0100.R10C6_LSR0,
         R10C5_H02E0401.R10C6_V00T0100,
         R10C4_V01N0101.R10C5_H02E0401,
         R11C4_JQ2.R10C4_V01N0101,
         R12C4_JDIC.R11C4_JQ2,
         R10C6_LSR0.R10C6_LSR0_SLICE,
         R12C4_JPADDIC_PIO.R12C4_JDIC;
   }
   signal q_c
   {

      // Writing 1 properties.
      property
      {
         TW_IS_CONST_SIG boolean true;
      } // End of property list.

      signal-pins
         // drivers
         (SLICE_0, Q0),
         // loads
         (q, PADDO);
      route
         R11C6_V02N0701.R11C6_JA2,
         R11C6_V02N0701.R11C6_V02S0700,
         R10C6_V01S0100.R11C6_V02S0700,
         R10C6_Q0.R10C6_V01S0100,
         R11C6_JA2.R12C6_JPADDOC,
         R12C6_JPADDOC.R12C6_PADDOC_PIO,
         R10C6_Q0_SLICE.R10C6_Q0;
   }
   signal r_c
   {
      signal-pins
         // drivers
         (r, PADDI),
         // loads
         (GSR_INST, GSR);
      route
         R1C6_H00R0300.R1C6_JC4,
         R1C6_V02S0101.R1C6_H00R0300,
         R1C6_V02N0100.R1C6_V02S0101,
         R1C9_H06W0103.R1C6_V02N0100,
         R1C12_JQ2.R1C9_H06W0103,
         R0C12_JDIC.R1C12_JQ2,
         R1C6_JC4.R1C4_JGSR_GSR,
         R0C12_JPADDIC_PIO.R0C12_JDIC;
   }
}
