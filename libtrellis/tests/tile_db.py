#!/usr/bin/env python3
import pytrellis

pytrellis.load_database("./testdata")
c = pytrellis.Chip("testdev")
bits = {
    (0, 0),
    (0, 3),
    (1, 0),
    (1, 3),
    (2, 0)
}
for b in bits:
    c.cram.set_bit(b[0], b[1], 1)

tcram = c.tiles["TEST_R0C0:TESTTILE"].cram
assert tcram.frames() == 20
assert tcram.bits() == 10

tl = pytrellis.TileLocator("test", "testdev", "TESTTILE")

tiledb = pytrellis.get_tile_bitdata(tl)
cfg = tiledb.tile_cram_to_config(tcram)
assert len(cfg.arcs) == 1
