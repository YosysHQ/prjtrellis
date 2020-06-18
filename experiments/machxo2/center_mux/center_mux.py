import diamond
from string import Template
import pytrellis
import shutil
import os

device = "LCMXO2-1200HC"

routes = [
    ("R1C13_JCLK0", "R6C13_JPCLKCIBVIQT0"),
    ("R6C13_JPCLKCIBVIQT0", "R6C13_PCLKCIBVIQT0"),
    ("R6C13_PCLKCIBVIQT0", "R6C13_VPRXCLKI0"),
    ("R6C13_VPRXCLKI0", "R6C13_CLKI0_DCC"),
    ("R6C13_CLKI0_DCC", "R6C13_CLKO0_DCC"),
    ("R6C13_CLKO0_DCC", "R6C13_VPRX0000"),
    ("R6C13_VPRX0000", "R6C8_HPSX0000"),
    ("R6C13_VPRX0000", "R6C18_HPSX0000"),
    ("R6C13_JLPLLCLK1", "R6C13_VPRXCLKI0"),
    ("R6C8_HPSX0000", "R6C10_CLKI0B_DCC"),
    ("R6C10_CLKI0B_DCC", "R6C10_CLKO0B_DCC"),
    ("R6C14_CLKI0B_DCC", "R6C14_CLKO0B_DCC"),
    ("R6C13_JTCDIVX1", "R6C13_VPRXCLKI5"),
    ("R6C13_PCLKCIBMID2", "R6C13_VPRXCLK60"),
    ("R6C13_PCLKCIBMID3", "R6C13_VPRXCLK61"),
    ("R6C13_PCLKCIBMID2", "R6C13_VPRXCLK71"),
    ("R6C13_PCLKCIBMID3", "R6C13_VPRXCLK70"),
    ("R6C13_JLPLLCLK0", "R6C13_EBRG0CLK0"),
    ("R6C13_JPCLKT20", "R6C13_EBRG0CLK0")
]

def run_get_tiles(mux_driver, sink):
    route = ""
    if mux_driver != "":
        route = "route\n\t\t\t" + mux_driver + "." + sink + ";"

    with open("center_mux_template.ncl", "r") as inf:
        with open("work/center_mux.ncl", "w") as ouf:
            ouf.write(Template(inf.read()).substitute(route=route))
    diamond.run(device, "work/center_mux.ncl")
    bs = pytrellis.Bitstream.read_bit("work/center_mux.bit")
    chip = bs.deserialise_chip()
    return chip.tiles


def main():
    pytrellis.load_database("../../../database")
    shutil.rmtree("work", ignore_errors=True)
    os.mkdir("work")
    baseline = run_get_tiles("", "")

    with open("center_mux_diff.txt", "w") as f:
        for r in routes:
            modified = run_get_tiles(r[0], r[1])

            tile_keys = []
            for t in modified:
                tile_keys.append(t.key())

            print("{0} -> {1}".format(r[0], r[1]), file=f)
            for k in tile_keys:
                diff = modified[k].cram - baseline[k].cram
                diff_str = ["{}F{}B{}".format("!" if b.delta < 0 else "", b.frame, b.bit) for b in diff]
                if not diff_str:
                    continue
                print("{0: <30}{1}".format(k, " ".join(diff_str)), file=f)
                f.flush()
            print("", file=f)

if __name__ == "__main__":
    main()
