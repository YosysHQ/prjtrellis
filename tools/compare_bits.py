#!/usr/bin/env python3
import sys, os, re

# Compare the output of a Lattice `bstool` dump  with ecpunpack and note discrepancies

if len(sys.argv) < 3:
    print("Usage: compare_bits.py lattice_dump.txt ecpunpack.out")
    sys.exit(2)

ecpup_re = re.compile(r'\((\d+), (\d+)\)')
lat_re = re.compile(r'^[A-Za-z0-9_/]+ \((\d+), (\d+)\)$')

ecpup_bits = []
lat_bits = []
with open(sys.argv[1], 'r') as latf:
    for line in latf:
        m = lat_re.match(line)
        if m:
            lat_bits.append((int(m.group(1)), int(m.group(2))))
print("Read {} bits from {}".format(len(lat_bits), sys.argv[1]))
with open(sys.argv[2], 'r') as upf:
    for line in upf:
        m = ecpup_re.match(line)
        if m:
            ecpup_bits.append((int(m.group(1)), int(m.group(2))))
print("Read {} bits from {}".format(len(ecpup_bits), sys.argv[2]))

ok = True

for b in ecpup_bits:
    if b not in lat_bits:
        print("In ecpunpack but not Lattice: ({}, {})".format(b[0], b[1]))
        ok = False
for b in lat_bits:
    if b not in ecpup_bits:
        print("In Lattice but not ecpunpack: ({}, {})".format(b[0], b[1]))
        ok = False

if ok:
    print("ecpunpack and Lattice match ({} bits compared)".format(len(ecpup_bits)))
else:
    sys.exit(1)