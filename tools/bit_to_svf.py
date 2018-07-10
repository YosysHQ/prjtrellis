#!/usr/bin/env python3

import sys
import textwrap

# Very basic bitstream to SVF converter, tested with the ULX3S WiFi interface

max_row_size = 8000 # needed for ULX3S Wifi
idcode = 0x41112043

def bitreverse(x):
    y = 0
    for i in range(8):
        if (x >> (7 - i)) & 1 == 1:
            y |= (1 << i)
    return y

with open(sys.argv[1], 'rb') as bitf:
    with open(sys.argv[2], 'w') as svf:
        print("""
HDR	0;
HIR	0;
TDR	0;
TIR	0;
ENDDR	DRPAUSE;
ENDIR	IRPAUSE;
FREQUENCY	1.00e+06 HZ;
STATE	IDLE;
        """, file=svf)
        print("""
SIR	8	TDI  (E0);
SDR	32	TDI  (00000000)
        TDO  ({:08X})
        MASK (FFFFFFFF);
        """.format(idcode), file=svf)
        print("""
SIR	8	TDI  (1C);
SDR	510	TDI  (3FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
             FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF);

SIR	8	TDI  (C6);
SDR	8	TDI  (00);
RUNTEST	IDLE	2 TCK	1.00E-02 SEC;

SIR	8	TDI  (3C);
SDR	32	TDI  (00000000)
        TDO  (00000000)
        MASK (0000B000);

SIR	8	TDI  (46);
SDR	8	TDI  (01);
RUNTEST	IDLE	2 TCK	1.00E-02 SEC;

SIR	8	TDI  (7A);
RUNTEST	IDLE	2 TCK	1.00E-02 SEC;

        """, file=svf)
        while True:
            chunk = bitf.read(max_row_size//8)
            if not chunk:
                break
            # Convert chunk to bit-reversed hex
            br_chunk = [bitreverse(x) for x in chunk]
            hex_chunk = ["{:02X}".format(x) for x in reversed(br_chunk)]
            print("\n".join(textwrap.wrap("SDR {} TDI ({});".format(8*len(chunk), "".join(hex_chunk)), 100)), file=svf)

        print("""
SIR	8	TDI  (FF);
RUNTEST	IDLE	100 TCK	1.00E-02 SEC;


SIR	8	TDI  (C0);
RUNTEST	IDLE	2 TCK	1.00E-03 SEC;
SDR	32	TDI  (00000000)
        TDO  (00000000)
        MASK (FFFFFFFF);

! Shift in ISC DISABLE(0x26) instruction
SIR	8	TDI  (26);
RUNTEST	IDLE	2 TCK	2.00E-01 SEC;
! Shift in BYPASS(0xFF) instruction
SIR	8	TDI  (FF);
RUNTEST	IDLE	2 TCK	1.00E-03 SEC;

! Shift in LSC_READ_STATUS(0x3C) instruction
SIR	8	TDI  (3C);
SDR	32	TDI  (00000000)
        TDO  (00000100)
        MASK (00002100);
        """, file=svf)
