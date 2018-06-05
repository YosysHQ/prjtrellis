::FROM-WRITER;
// designname: top
// Creation time stamp: 05/05/18  14:52:34
design top
{
   device
   {
      architecture sa5p00;
      device LFE5U-25F;
      package CABGA381;
      performance "8";
   }

   // Writing 12 properties. 
   property
   {
      LSE_CPS_MAP_FILE string "xxx_lse_sign_file";
      "PINNAME:0" string "a";
      "PINNAME:1" string "b";
      "PINNAME:2" string "c";
      "PINNAME:3" string "d";
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
      //       D0 --> A0      
      //       C0 --> B0      
      //       B0 --> D0      
      //       A0 --> C0      
      [,,,,A0,B0,D0,C0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,]
   {

      // Writing 2 properties. 
      property
      {
         LSE_CPS_ID_1 string "K0";
         NGID0 long 1;
      } // End of property list.

      logical
      {
         cellmodel-name SLICE;
         program "MODE:LOGIC "
                 "K0::H0=0 "
                 "F0:F ";
         primitive K0 i3_4_lut;
      }
      site R2C2A;
   }
   comp q
   {

      // Writing 3 properties. 
      property
      {
         "#%PAD%PINID" long 4;
         LSE_CPS_ID_2 string "IOBUF";
         NGID0 long 5;
      } // End of property list.

      logical
      {
         cellmodel-name PIO;
         program "TRIMUX:PADDT:::PADDT=0 "
                 "IOBUF:::PULLMODE=NONE,DRIVE=8, \"
                    "SLEWRATE=SLOW,CLAMP=ON,HYSTERESIS=NA "
                 "DATAMUX:PADDO "
                 "VREF:OFF "
                 "ODMUX:TRIMUX "
                 "LVDSMUX:DATAMUX ";
         primitive IOBUF q_pad;
         primitive PAD q;
      }
      site P4;
   }
   comp "a"
   {

      // Writing 3 properties. 
      property
      {
         "#%PAD%PINID" long 0;
         LSE_CPS_ID_3 string "IOBUF";
         NGID0 long 6;
      } // End of property list.

      logical
      {
         cellmodel-name PIO;
         program "PADDI:PADDI "
                 "IOBUF:::CLAMP=ON "
                 "VREF:OFF "
                 "INRDMUX:INBUF "
                 "MIPIMUX:INRDMUX ";
         primitive IOBUF a_pad;
         primitive PAD "a";
      }
      site T1;
   }
   comp b
   {

      // Writing 3 properties. 
      property
      {
         "#%PAD%PINID" long 1;
         LSE_CPS_ID_4 string "IOBUF";
         NGID0 long 7;
      } // End of property list.

      logical
      {
         cellmodel-name PIO;
         program "PADDI:PADDI "
                 "IOBUF:::CLAMP=ON "
                 "VREF:OFF "
                 "INRDMUX:INBUF "
                 "MIPIMUX:INRDMUX ";
         primitive IOBUF b_pad;
         primitive PAD b;
      }
      site P2;
   }
   comp c
   {

      // Writing 3 properties. 
      property
      {
         "#%PAD%PINID" long 2;
         LSE_CPS_ID_5 string "IOBUF";
         NGID0 long 8;
      } // End of property list.

      logical
      {
         cellmodel-name PIO;
         program "PADDI:PADDI "
                 "IOBUF:::CLAMP=ON "
                 "VREF:OFF "
                 "INRDMUX:INBUF "
                 "MIPIMUX:INRDMUX ";
         primitive IOBUF c_pad;
         primitive PAD c;
      }
      site P1;
   }
   comp d
   {

      // Writing 3 properties. 
      property
      {
         "#%PAD%PINID" long 3;
         LSE_CPS_ID_6 string "IOBUF";
         NGID0 long 9;
      } // End of property list.

      logical
      {
         cellmodel-name PIO;
         program "PADDI:PADDI "
                 "IOBUF:::CLAMP=ON "
                 "VREF:OFF "
                 "INRDMUX:INBUF "
                 "MIPIMUX:INRDMUX ";
         primitive IOBUF d_pad;
         primitive PAD d;
      }
      site P3;
   }
   // The Design Signals. 
   signal a_c
   {
      signal-pins
         // drivers
         ("a", PADDI),
         // loads
         (SLICE_0, D0);
   }
   signal b_c
   {
      signal-pins
         // drivers
         (b, PADDI),
         // loads
         (SLICE_0, C0);
   }
   signal d_c
   {
      signal-pins
         // drivers
         (d, PADDI),
         // loads
         (SLICE_0, A0);
   }
   signal c_c
   {
      signal-pins
         // drivers
         (c, PADDI),
         // loads
         (SLICE_0, B0);
   }
   signal q_c
   {
      signal-pins
         // drivers
         (SLICE_0, F0),
         // loads
         (q, PADDO);
   }
}
