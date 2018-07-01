#!/usr/bin/env python3
import diamond
from string import Template
import re
device = "LFE5U-45F"

ncl = """
::FROM-WRITER;
design top
{
   device
   {
      architecture sa5p00;
      device LFE5U-25F;
      package CABGA381;
      performance "8";
   }

   comp SLICE_0
      [,,,,A0,B0,D0,C0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,]
   {
      logical
      {
         cellmodel-name SLICE;
         program "MODE:LOGIC "
                 "K0::H0=0 "
                 "K1::H1=0 "
                 "F0:F "
                 "F1:F ";
         primitive K0 i3_0_lut;
         primitive K1 i3_1_lut;
         
      }
      site R6C10A;
   }

   comp SLICE_1
      [,,,,A0,B0,D0,C0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,]
   {
      logical
      {
         cellmodel-name SLICE;
         program "MODE:LOGIC "
                 "K0::H0=0 "
                 "K1::H1=0 "
                 "F0:F "
                 "F1:F ";
         primitive K0 i4_0_lut;
         primitive K1 i4_1_lut;
      }
      site R6C10B;
   }
   
   comp SLICE_2
   [,,,,A0,B0,D0,C0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,]
   {
      logical
      {
         cellmodel-name SLICE;
         program "MODE:LOGIC "
                 "K0::H0=0 "
                 "K1::H1=0 "
                 "F0:F "
                 "F1:F ";
         primitive K0 i5_0_lut;
         primitive K1 i5_1_lut;
      }
      site R6C10C;
   }
   
   comp SLICE_3
   [,,,,A0,B0,D0,C0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,]
   {
      logical
      {
         cellmodel-name SLICE;
         program "MODE:LOGIC "
                 "K0::H0=0 "
                 "K1::H1=0 "
                 "F0:F "
                 "F1:F ";
         primitive K0 i6_0_lut;
         primitive K1 i6_1_lut;
      }
      site R6C10D;
   }

   comp SLICE_4
   [,,,,A0,B0,D0,C0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,]
   {
      logical
      {
         cellmodel-name SLICE;
         program "MODE:LOGIC "
                 "K0::H0=0 "
                 "K1::H1=0 "
                 "F0:F "
                 "F1:F ";
         primitive K0 i6_0_lut;
         primitive K1 i6_1_lut;
      }
      site R6C12C;
   }

    signal q_c
   {
      signal-pins
         // drivers
         (SLICE_4, F1),
         // loads
         $loads;
      route
         $route;
   }
}
"""

sinks = [
    ("(SLICE_0, A0)", "A0"),
    ("(SLICE_0, A1)", "A1"),
    ("(SLICE_1, A0)", "A2"),
    ("(SLICE_1, A1)", "A3"),
    ("(SLICE_2, A0)", "A4"),
    ("(SLICE_2, A1)", "A5"),
    ("(SLICE_3, A0)", "A6"),
    ("(SLICE_3, A1)", "A7"),
]

timings = []

for i in range(1, 9):
    loads = [sinks[j][0] for j in range(i)]
    route = ["R6C12_F5_SLICE.R6C12_F5",
             "R6C12_F5.R6C11_H02W0501"]
    for j in range(i):
        destwire = sinks[j][1]
        route.append("R6C11_H02W0501.R6C10_{}".format(destwire))
        route.append("R6C10_{}.R6C10_{}_SLICE".format(destwire, destwire))
    loads_txt = ",         \n".join(loads)
    route_txt = ",         \n".join(route)
    desfile = "fanout_{}.ncl".format(i)
    with open(desfile, "w") as ouf:
        ouf.write(Template(ncl).substitute(loads=loads_txt, route=route_txt))
    diamond.run(device, desfile)
    with open(desfile.replace("ncl", "twr"), "r") as twrf:
        for line in twrf:
            m = re.match(r"\s+([0-9.]+)ns\s+R6C12C\.F1 to R6C10A\.A0\s+", line)
            if m:
                timings.append(float(m.group(1)))
print("")
print("")
print("Fanout\tDelay")
for i in range(len(timings)):
    print("{}\t{}".format(i+1, timings[i]))
