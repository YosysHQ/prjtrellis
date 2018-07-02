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
      device LFE5U-45F;
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
      site R7C10A;
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
      site R${row}C10C;
   }

    signal q_c
   {
      signal-pins
         // drivers
         (SLICE_4, F1),
         // loads
         (SLICE_0, A0);
      route
         $route;
   }
}
"""

timings = []

for i in range(0, 60, 2):
    row = 7 + i
    nets = ["R{}C10_F5_SLICE".format(row), "R{}C10_F5".format(row)]
    for j in range(0, i, 2):
        nets.append("R{}C10_V02N0701".format(row - (j + 1)))
    nets.append("R7C10_A0")
    nets.append("R7C10_A0_SLICE")
    route = []
    for k in range(len(nets) - 1):
        route.append("{}.{}".format(nets[k], nets[k+1]))

    route_txt = ",         \n".join(route)
    desfile = "distance_{}.ncl".format(i)
    with open(desfile, "w") as ouf:
        ouf.write(Template(ncl).substitute(row=row, route=route_txt))
    diamond.run(device, desfile)
    with open(desfile.replace("ncl", "twr"), "r") as twrf:
        for line in twrf:
            m = re.match(r"\s+([0-9.]+)ns\s+R\d+C\d+C\.F1 to R7C10A\.A0\s+", line)
            if m:
                timings.append(float(m.group(1)))
print("")
print("")
print("Length\tDelay")
for i in range(len(timings)):
    print("{}\t{}".format(2*i, timings[i]))
