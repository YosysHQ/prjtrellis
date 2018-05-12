#!/usr/bin/env python3
import pytrellis

pytrellis.load_database("./testdata")
c = pytrellis.Chip("testdev")
bits = {
    (0, 0),
    (15, 10),
    (34, 11),
    (34, 19)
}
for b in bits:
    c.cram.set_bit(b[0], b[1], 1)

tcram = c.tiles["TEST_R0C0:TESTTILE"].cram
assert tcram.frames() == 20
assert tcram.bits() == 10

for f in range(tcram.frames()):
    for b in range(tcram.bits()):
        if (f + 10, b + 15) in bits:
            assert tcram.bit(f, b)
        else:
            assert not tcram.bit(f, b)
