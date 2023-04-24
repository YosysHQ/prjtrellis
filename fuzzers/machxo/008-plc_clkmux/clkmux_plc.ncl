::FROM-WRITER;
// designname: top
// Creation time stamp: 04/24/23  12:38:35
design top
{
   device
   {
      architecture mj5g00;
      device LCMXO2280C;
      package TQFP100;
      performance "3";
   }

   // Writing 11 properties. 
   property
   {
      "Operating Condition" string "COMMERCIAL";
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
   } // End of property list.

   // The Design macro definitions. 
   // The Design macro instances.
   // The Design Comps. 
   comp SLICE_0
   {

      // Writing 1 properties. 
      property
      {
         NGID0 long 3;
      } // End of property list.

      logical
      {
         cellmodel-name FSLICE;
         program "REGMODE:FF "
                 "MODE:LOGIC "
                 "REG0:::REGSET=SET:SD=0 "
                 "Q0:Q "
                 "GSR:ENABLED "
                 "M0MUX:M0 "
                 "CLKMUX:${clkmux} "
                 "CEMUX:1:::1=0 "
                 "LSRMUX:LSR "
                 "SRMODE:LSR_OVER_CE "
                 "LSRONMUX:LSRMUX ";
         primitive REG0 ff;
      }
      site R9C5C;
   }
   comp q
   {

      // Writing 1 properties. 
      property
      {
         "#%PAD%PINID" long 4;
      } // End of property list.

      logical
      {
         cellmodel-name PIO;
         program "IOBUF:::DRIVE=12 "
                 "DATAMUX:PADDO "
                 "TRIMUX:PADDT:::PADDT=0 "
                 "TRIINV:TRIMUX ";
         primitive IOBUF q_pad;
         primitive PAD q;
      }
      site "10";
   }
   comp d
   {

      // Writing 1 properties. 
      property
      {
         "#%PAD%PINID" long 1;
      } // End of property list.

      logical
      {
         cellmodel-name PIO;
         program "PADDI:PADDI "
                 "IOBUF:#ON "
                 "INDELMUX:INBUF ";
         primitive IOBUF d_pad;
         primitive PAD d;
      }
      site "13";
   }
   comp s
   {

      // Writing 1 properties. 
      property
      {
         "#%PAD%PINID" long 3;
      } // End of property list.

      logical
      {
         cellmodel-name PIO;
         program "PADDI:PADDI "
                 "IOBUF:#ON "
                 "INDELMUX:INBUF ";
         primitive IOBUF s_pad;
         primitive PAD s;
      }
      site "11";
   }
   comp r
   {

      // Writing 1 properties. 
      property
      {
         "#%PAD%PINID" long 2;
      } // End of property list.

      logical
      {
         cellmodel-name PIO;
         program "PADDI:PADDI "
                 "IOBUF:#ON "
                 "INDELMUX:INBUF ";
         primitive IOBUF r_pad;
         primitive PAD r;
      }
      site "57";
   }
   comp gsr
   {

      // Writing 1 properties. 
      property
      {
         NGID0 long 4;
      } // End of property list.

      logical
      {
         cellmodel-name GSR;
         program "GSRMODE:ACTIVE_LOW ";
      }
      site GSR;
   }
   // The Design Signals. 
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
         R9C0_JDDTD1C.R9C0_JPADDOC,
         R9C1_JB5.R9C0_JDDTD1C,
         R9C1_H02W0601.R9C1_JB5,
         R9C1_H06E0205.R9C1_H02W0601,
         R9C3_H06W0202.R9C1_H06E0205,
         R9C5_Q4.R9C3_H06W0202,
         R9C0_JPADDOC.R9C0_JPADDOC_PIO,
         R9C5_JQ4_SLICE.R9C5_Q4;
   }
   signal d_c
   {
      signal-pins
         // drivers
         (d, PADDI),
         // loads
         (SLICE_0, M0);
      route 
         R9C6_H02W0401.R9C5_M4,
         R9C4_H06E0203.R9C6_H02W0401,
         R9C1_V01N0101.R9C4_H06E0203,
         R10C1_JOFX7.R9C1_V01N0101,
         R9C5_M4.R9C5_M4_SLICE,
         R10C0_JPADDID_PIO.R10C1_JOFX7;
   }
   signal s_c
   {
      signal-pins
         // drivers
         (s, PADDI),
         // loads
         (SLICE_0, LSR);
      route 
         R9C6_H02W0701.R9C5_LSR2,
         R9C4_H06E0303.R9C6_H02W0701,
         R9C1_JOFX7.R9C4_H06E0303,
         R9C5_LSR2.R9C5_LSR2_SLICE,
         R9C0_JPADDID_PIO.R9C1_JOFX7;
   }
   signal r_c
   {
      signal-pins
         // drivers
         (r, PADDI),
         // loads
         (gsr, GSR);
      route 
         R14C17_H02E0301.R14C17_JC2,
         R14C16_V02N0301.R14C17_H02E0301,
         R15C16_H02W0301.R14C16_V02N0301,
         R15C17_JF1.R15C16_H02W0301,
         R14C17_JC2.R14C17_JGSR_GSR,
         R15C18_JPADDIB_PIO.R15C17_JF1;
   }
}
