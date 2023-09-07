from nets import net_product, char_range
from itertools import product, starmap
from collections import defaultdict
import re

def io_conns(tile, bank, ab_only=False):
    # All I/O connections on the left bank are contained in the other banks.
    all_template = [
        ("JPADDO{}", "sink"),
        ("JPADDT{}", "sink"),
        ("PADDO{}_PIO", "sink"),
        ("PADDT{}_PIO", "sink"),
        ("IOLDO{}_PIO","sink"),
        ("IOLDO{}_{}IOLOGIC","sink"),
        ("IOLTO{}_PIO","sink"),
        ("IOLTO{}_{}IOLOGIC","sink"),
        ("JPADDI{}_PIO", "driver"),
        ("PADDI{}_{}IOLOGIC", "driver"),
        ("JDI{}", "driver"),
        ("INDD{}_{}IOLOGIC", "driver"),
        ("DI{}_{}IOLOGIC", "sink"),
        ("JONEG{}_{}IOLOGIC", "sink"),
        ("JOPOS{}_{}IOLOGIC", "sink"),
        ("JTS{}_{}IOLOGIC", "sink"),
        ("JCE{}_{}IOLOGIC", "sink"),
        ("JLSR{}_{}IOLOGIC", "sink"),
        ("JCLK{}_{}IOLOGIC", "sink"),
        ("JIN{}_{}IOLOGIC", "driver"),
        ("JIP{}_{}IOLOGIC", "driver"),
        ("INRD{}_PIO", "sink"),
        ("PG{}_PIO", "sink"),
        ("LVDS{}_PIO", "sink")
    ]

    right = [
        ("DQSW90{}_RIOLOGIC", "sink"),
        ("DQSR90{}_RIOLOGIC", "sink"),
        ("DDRCLKPOL{}_RIOLOGIC", "sink")
    ]

    bottom = [
        ("JRXDA{2}_{1}IOLOGIC", "driver"),
        ("JRXD{2}{0}_{1}IOLOGIC", "driver"),
        ("JDEL{2}{0}_{1}IOLOGIC", "sink"),
        ("JSLIP{}_{}IOLOGIC", "sink"),
        ("ECLK{}_{}IOLOGIC", "sink"),
        ("ECLK{}", "sink"),
    ]

    top = [
        ("JTXD{2}{0}_{1}IOLOGIC", "sink"),
        ("ECLK{}_{}IOLOGIC", "sink"),
        ("ECLK{}", "sink"),
    ]

    if bank == "B":
        bank_template = bottom
    elif bank == "T":
        bank_template = top
    elif bank.startswith("R"):
        bank_template = right
    else:
        bank_template = []

    # Nets which come in 0-3/0-7 and 0-4, respectively.
    rxda_re = re.compile("JRXDA\{2\}*")
    rxd_re = re.compile("JRXD\{2\}\{0\}*")
    txda_re = re.compile("JTXD\{2\}A*")
    txd_re = re.compile("JTXD\{2\}\{0\}*")
    del_re = re.compile("JDEL*")
    eclk_re = re.compile("ECLKC*")

    netlist = []
    if ab_only:
        pads = ("A", "B")
    else:
        pads = ("A", "B", "C", "D")

    for pad in pads:
        # B/BS/T/TSIOLOGIC
        if bank in ("B", "T"):
            if pad == "A":
                io_prefix = bank
            elif pad == "C":
                io_prefix = "{}S".format(bank)
            else:
                io_prefix = ""
        # RIOLOGIC
        elif bank.startswith("R"):
            io_prefix = "R"
        # Just "LOGIC"
        else:
            io_prefix = ""

        for f, d in all_template:
            suffix = f.format(pad, io_prefix)
            netlist.append(("R{}C{}_{}".format(tile[0], tile[1], suffix), d))

        if bank.startswith("R"):
            for f, d in bank_template:
                suffix = f.format(pad, io_prefix)
                netlist.append(("R{}C{}_{}".format(tile[0], tile[1], suffix), d))
        elif bank == "B":
            for f, d in bank_template:
                if del_re.match(f) and pad in ("A", "C"):
                    for n in range(5):
                        suffix = f.format(pad, io_prefix, n)
                        netlist.append(("R{}C{}_{}".format(tile[0], tile[1], suffix), d))
                elif rxda_re.match(f) and pad == "A":
                    for n in range(8):
                        suffix = f.format(pad, io_prefix, n)
                        netlist.append(("R{}C{}_{}".format(tile[0], tile[1], suffix), d))
                elif rxd_re.match(f) and pad in ("A", "C"):
                    for n in range(4):
                        suffix = f.format(pad, io_prefix, n)
                        netlist.append(("R{}C{}_{}".format(tile[0], tile[1], suffix), d))
                elif pad in ("A", "C") and not rxda_re.match(f):
                    suffix = f.format(pad, io_prefix)
                    netlist.append(("R{}C{}_{}".format(tile[0], tile[1], suffix), d))
#            netlist.append(("R{}C{}_BECLK0".format(tile[0], tile[1]), "sink"))
#            netlist.append(("R{}C{}_BECLK1".format(tile[0], tile[1]), "sink"))
        elif bank == "T":
            for f, d in bank_template:
                if txd_re.match(f) and pad in ("A", "C"):
                    netrange = range(8) if pad == "A" else range(4)
                    for n in netrange:
                        suffix = f.format(pad, io_prefix, n)
                        netlist.append(("R{}C{}_{}".format(tile[0], tile[1], suffix), d))
                elif eclk_re.match(f) and pad in ("A", "C"):
                    suffix = f.format(pad, io_prefix)
                    netlist.append(("R{}C{}_{}".format(tile[0], tile[1], suffix), d))
                elif not txd_re.match(f) and not eclk_re.match(f):
                    suffix = f.format(pad, io_prefix)
                    netlist.append(("R{}C{}_{}".format(tile[0], tile[1], suffix), d))
#            netlist.append(("R{}C{}_TECLK0".format(tile[0], tile[1]), "sink"))
#            netlist.append(("R{}C{}_TECLK1".format(tile[0], tile[1]), "sink"))

    return netlist

def main():
    for t, b, ab in zip(
        ((10, 0), (12, 11), (10, 23), (1, 11), (9, 0), (3, 23)),
        ("L", "B", "R", "T", "LS", "RS"),
        (False, False, False, False, True, True)):
            print("Bank {} (AB only={}):".format(b, ab))
            for i, n in enumerate(io_conns(t, b, ab)):
                print(i, n)
            print("")

if __name__ == "__main__":
    main()
