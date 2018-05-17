#!/usr/bin/env python3
import pytrellis

pytrellis.load_database("./testdata")
c = pytrellis.Chip("testdev")

assert c.get_max_row() == 0
assert c.get_max_col() == 0

bits = {
    (0, 0),
    (0, 3),
    (1, 0),
    (1, 2),
    (2, 0),
    (5, 3)
}
for b in bits:
    c.cram.set_bit(10 + b[0], 15 + b[1], 1)

tcram = c.tiles["TEST_R0C0:TESTTILE"].cram
assert tcram.frames() == 20
assert tcram.bits() == 10

tl = pytrellis.TileLocator("test", "testdev", "TESTTILE")

tiledb = pytrellis.get_tile_bitdata(tl)
cfg = tiledb.tile_cram_to_config(tcram)
assert len(cfg.carcs) == 1
assert cfg.carcs[0].source == "H2" and cfg.carcs[0].sink == "A0"
assert len(cfg.cwords) == 1
assert cfg.cwords[0].name == "INIT" and list(cfg.cwords[0].value) == [0, 1, 0, 1]
assert len(cfg.cenums) == 1
assert cfg.cenums[0].name == "MODE" and cfg.cenums[0].value == "CARRY"
assert len(cfg.cunknowns) == 1
assert cfg.cunknowns[0].frame == 5 and cfg.cunknowns[0].bit == 3
