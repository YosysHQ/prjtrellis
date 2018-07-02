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
      site R6C10A;
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
      site R6C${col}C;
   }

    signal q_c
   {
      signal-pins
         // drivers
         (SLICE_4, F1),
         // loads
         (SLICE_0, B0);
      route
         $route;
   }
}
"""

timings = []

for i in range(0, 79, 6):
    col = 10 + i
    nets = ["R6C{}_F5_SLICE".format(col), "R6C{}_F5".format(col)]
    for j in range(0, i, 6):
        nets.append("R6C{}_H06W0303".format(col - (j + 3)))
    nets.append("R6C10_H01W0100")
    nets.append("R6C10_B0")
    nets.append("R6C10_B0_SLICE")
    route = []
    for k in range(len(nets) - 1):
        route.append("{}.{}".format(nets[k], nets[k + 1]))

    route_txt = ",         \n".join(route)
    desfile = "distance_{}.ncl".format(i)
    with open(desfile, "w") as ouf:
        ouf.write(Template(ncl).substitute(col=col, route=route_txt))
    diamond.run(device, desfile)
    with open(desfile.replace("ncl", "twr"), "r") as twrf:
        for line in twrf:
            m = re.match(r"\s+([0-9.]+)ns\s+R6C\d+C\.F1 to R6C10A\.B0\s+", line)
            if m:
                timings.append(float(m.group(1)))
print("")
print("")
print("Length\tDelay")
for i in range(len(timings)):
    print("{}\t{}".format(6 * i, timings[i]))
