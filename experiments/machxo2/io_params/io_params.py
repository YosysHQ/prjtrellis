import diamond
from string import Template
import pytrellis
import shutil
import os
import argparse

device = "LCMXO2-1200HC"

def run_get_tiles(dir, io_type="LVCMOS33", loc="PB11D"):
    with open("io_params_template.v", "r") as inf:
        with open("work/io_params.v", "w") as ouf:
            ouf.write(Template(inf.read()).substitute(dir=dir,
                io_type="\"" + io_type + "\"", loc= "\"" + loc + "\""))
    diamond.run(device, "work/io_params.v")
    bs = pytrellis.Bitstream.read_bit("work/io_params.bit")
    chip = bs.deserialise_chip()
    return chip.tiles


def main(args):
    pytrellis.load_database("../../../database")
    shutil.rmtree("work", ignore_errors=True)
    os.mkdir("work")
    os.environ['DEV_PACKAGE'] = args.p
    baseline = run_get_tiles("NONE", args.io_type, args.loc)

    dirs = []

    if args.b:
        dirs.append("BIDIR")
    if args.i:
        dirs.append("INPUT")
    if args.o:
        dirs.append("OUTPUT")

    with open("io_params_diff.txt", "w") as f:
        for d in dirs:
            modified = run_get_tiles(d, args.io_type, args.loc)

            tile_keys = []
            for t in modified:
                tile_keys.append(t.key())

            print("{0}".format(d), file=f)
            for k in tile_keys:
                diff = modified[k].cram - baseline[k].cram
                diff_str = ["{}F{}B{}".format("!" if b.delta < 0 else "", b.frame, b.bit) for b in diff]
                if not diff_str:
                    continue
                print("{0: <30}{1}".format(k, " ".join(diff_str)), file=f)
                f.flush()
            print("", file=f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test I/O Site")
    parser.add_argument("-b", help="Test bidirectional.", action="store_true")
    parser.add_argument("-i", help="Test input.", action="store_true")
    parser.add_argument("-o", help="Test output.", action="store_true")
    parser.add_argument("-p", type=str, default="QFN32", help="Device package to test.")
    parser.add_argument(dest="io_type", type=str, default="LVCMOS33", help="I/O standard to test.")
    parser.add_argument(dest="loc", type=str, default="PB11D", help="Site to test.")
    args = parser.parse_args()

    main(args)
