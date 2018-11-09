#!/usr/bin/env python3
"""
Convert the tile grid for a given family and device to HTML format
"""
import sys, re
import argparse
import database

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('family', type=str,
                    help="FPGA family (e.g. ECP5)")
parser.add_argument('device', type=str,
                    help="FPGA device (e.g. LFE5U-85F)")
parser.add_argument('outfile', type=argparse.FileType('w'),
                    help="output HTML file")

rc_regex = re.compile(r"[A-Za-z0-9_]*R(\d+)C(\d+)")
# MachXO2-specific
center_regex = re.compile(r"CENTER(\d+)")
centerb_regex = re.compile(r"CENTER_B")
centert_regex = re.compile(r"CENTER_T")
centerebr_regex = re.compile(r"CENTER_EBR(\d+)")
t_regex = re.compile(r"[A-Za-z0-9_]*T(\d+)")
b_regex = re.compile(r"[A-Za-z0-9_]*B(\d+)")
l_regex = re.compile(r"[A-Za-z0-9_]*L(\d+)")
r_regex = re.compile(r"[A-Za-z0-9_]*R(\d+)")


# FIXME: This only works for MachXO2-1200, because we don't know in general
# how many rows/cols an MachXO2 device will have without knowing the part
# number.
def get_rc(name):
    # Match in order of most-specific to least-specific
    # (E.g. CENTER matches "R" regex too)
    rc = rc_regex.match(name)
    if rc:
        row = int(rc.group(1))
        col = int(rc.group(2))
        return (row, col)

    centert = centert_regex.match(name)
    if centert:
        row = 0
        col = 13
        return (row, col)

    centerb = centerb_regex.match(name)
    if centerb:
        row = 12
        col = 13
        return (row, col)

    centerebr = centerebr_regex.match(name)
    if centerebr:
        row = 6
        col = 14
        return (row, col)

    center = center_regex.match(name)
    if center:
        row = int(center.group(1))
        col = 13
        return (row, col)

    t = t_regex.match(name)
    if t:
        row = 0
        col = int(t.group(1))
        return (row, col)

    b = b_regex.match(name)
    if b:
        row = 12
        col = int(b.group(1))
        return (row, col)

    l = l_regex.match(name)
    if l:
        row = int(l.group(1))
        col = 0
        return (row, col)

    r = r_regex.match(name)
    if r:
        row = int(r.group(1))
        col = 23
        return (row, col)


def get_colour(ttype):
    colour = "#FFFFFF"
    if ttype.startswith("PIO"):
        colour = "#88FF88"
    elif ttype.startswith("PIC"):
        colour = "#88FFFF"
    elif ttype.startswith("CIB"):
        colour = "#FF8888"
    elif ttype.startswith("PLC"):
        colour = "#8888FF"
    elif ttype.startswith("DUMMY"):
        colour = "#FFFFFF"
    elif ttype.startswith("MIB_EBR") or ttype.startswith("EBR_SPINE"):
        colour = "#FF88FF"
    elif ttype.find("DSP") != -1:
        colour = "#FFFF88"
    elif ttype.find("TAP") != -1:
        colour = "#DDDDDD"
    else:
        colour = "#888888"
    return colour


def main(argv):
    args = parser.parse_args(argv[1:])
    tilegrid = database.get_tilegrid(args.family, args.device)

    max_row = 0
    max_col = 0
    for name in sorted(tilegrid.keys()):
        row, col = get_rc(name)
        if row > max_row: max_row = row
        if col > max_col: max_col = col

    tiles = []
    for i in range(max_row + 1):
        row = []
        for j in range(max_col + 1):
            row.append([])
        tiles.append(row)

    for identifier, data in sorted(tilegrid.items()):
        name = identifier.split(":")[0]
        row, col = get_rc(name)
        colour = get_colour(data["type"])
        tiles[row][col].append((name, data["type"], colour))

    f = args.outfile
    print(
        """<html>
            <head><title>{} Tiles</title></head>
            <body>
            <h1>{} Tilegrid</h1>
            <table style='font-size: 8pt; border: 2px solid black; text-align: center'>
        """.format(args.device, args.device), file=f)
    for trow in tiles:
        print("<tr>", file=f)
        row_max_height = 0
        for tloc in trow:
            row_max_height = max(row_max_height, len(tloc))
        row_height = max(75, 30 * row_max_height)
        for tloc in trow:
            print("<td style='border: 2px solid black; height: {}px'>".format(row_height), file=f)
            for tile in tloc:
                print(
                    "<div style='height: {}%; background-color: {}'><em>{}</em><br/><strong><a href='../tilehtml/{}.html' style='color: black'>{}</a></strong></div>".format(
                        100 / len(tloc), tile[2], tile[0], tile[1], tile[1]), file=f)
            print("</td>", file=f)
        print("</tr>", file=f)
    print("</table></body></html>", file=f)


if __name__ == "__main__":
    main(sys.argv)
