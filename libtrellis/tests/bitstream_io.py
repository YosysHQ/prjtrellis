import pytrellis

pytrellis.load_database("./testdata")
c = pytrellis.Chip("testdev")
bits = {
    (0, 0),
    (10, 0),
    (399, 0),
    (0, 98),
    (399, 97)
}
for b in bits:
    c.cram.set_bit(b[0], b[1], 1)

bs = pytrellis.Bitstream.serialise_chip(c)
bs.metadata.append("test_metadata")
bs.write_bit("work/bitstream_io.bit")

bs2 = pytrellis.Bitstream.read_bit("work/bitstream_io.bit")
assert(list(bs2.metadata) == ["test_metadata"])
c2 = bs2.deserialise_chip()
for f in range(c2.cram.frames()):
    for b in range(c2.cram.bits()):
        if (f, b) in bits:
            assert c2.cram.bit(f, b)
        else:
            assert not c2.cram.bit(f, b)

