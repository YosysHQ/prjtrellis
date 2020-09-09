import diamond
from string import Template
import pytrellis
import shutil
import os

# With this experiment, I concluded that CCU2 doesn't really control any bits.
# This experiment doesn't run as-is- add.bit/sub.bit are missing. I may re-add
# them later.

device = "LCMXO2-1200HC"

def run_get_tiles(muxcfg):
    with open("ccu2_template.ncl", "r") as inf:
        with open("work/ccu2.ncl", "w") as ouf:
            ouf.write(Template(inf.read()).substitute(muxcfg=muxcfg))
    diamond.run(device, "work/ccu2.ncl")
    bs = pytrellis.Bitstream.read_bit("work/ccu2.bit")
    chip = bs.deserialise_chip()
    return chip.tiles


def main():
    pytrellis.load_database("../../../database")
    shutil.rmtree("work", ignore_errors=True)
    os.mkdir("work")
    baseline = run_get_tiles("::B0=0,C0=0,D0=0,A1=0,B1=0,C1=0,D1=0 ")

    # baseline = pytrellis.Bitstream.read_bit("../../../minitests/math/add.bit").deserialise_chip().tiles
    # modified = pytrellis.Bitstream.read_bit("../../../minitests/math/sub.bit").deserialise_chip().tiles

    with open("ccu2_diff.txt", "w") as f:
        for m in ["::A0=0,B0=0,C0=0,D0=0,B1=0,C1=0,D1=0 "]:
            modified = run_get_tiles(m)

        tile_keys = []
        for t in modified:
            tile_keys.append(t.key())

        for k in tile_keys:
            diff = modified[k].cram - baseline[k].cram
            diff_str = ["{}F{}B{}".format("!" if b.delta < 0 else "", b.frame, b.bit) for b in diff]
            print("{0: <18}{1}".format(k, " ".join(diff_str)), file=f)
            f.flush()


if __name__ == "__main__":
    main()
