# Pastebin J2L5zfiT
#!/usr/bin/env python3
import sys
import json
import argparse
import pytrellis
import database

# (X, Y, Z)
def get_bel(pin, info):
    assert pin[0] == "P"
    edge = pin[1]
    pos = int(pin[2:-1])
    pio = pin[-1]
    if edge == "T":
        return (pos - info.col_bias, 0, pio)
    elif edge == "B":
        return (pos - info.col_bias, max_row, pio)
    elif edge == "L":
        return (0, pos - info.row_bias, pio)
    elif edge == "R":
        return (max_col, pos - info.row_bias, pio)
    else:
        assert False

def main(args):
    global max_row, max_col

    pytrellis.load_database(database.get_db_root())
    chip = pytrellis.Chip(args.device)

    max_row = chip.get_max_row()
    max_col = chip.get_max_col()

    if chip.info.family.startswith("MachXO"):
        # I/O Grouping is present in MachXO2 pinouts but not ECP5.
        pkg_index_start = 8
    else:
        pkg_index_start = 7

    metadata = dict()
    package_data = dict()
    package_indicies = None
    found_header = False
    with args.infile as csvf:
        for line in csvf:
            trline = line.strip()
            splitline = trline.split(",")
            if len(splitline) < (pkg_index_start + 1):
                continue
            if len(splitline[0].strip()) == 0:
                continue
            if splitline[0] == "PAD":
                # is header
                found_header = True
                package_indicies = splitline[pkg_index_start:]
                for pkg in package_indicies:
                    package_data[pkg] = {}
            elif found_header:
                if splitline[1][0] != "P" or splitline[1].startswith("PROGRAM"):
                    continue
                bel = get_bel(splitline[1], chip.info)
                bank = int(splitline[2])
                function = splitline[3]
                dqs = splitline[6]
                if chip.info.family.startswith("MachXO"):
                    io_grouping = splitline[7]
                    metadata[bel] = bank, function, dqs, io_grouping
                else:
                    metadata[bel] = bank, function, dqs
                for i in range(len(package_indicies)):
                    if splitline[pkg_index_start+i] == "-":
                        continue
                    package_data[package_indicies[i]][splitline[pkg_index_start+i]] = bel
    json_data = {"packages": {}, "pio_metadata": []}
    for pkg, pins in package_data.items():
        json_data["packages"][pkg] = {}
        for pin, bel in pins.items():
            json_data["packages"][pkg][pin] = {"col": bel[0], "row": bel[1], "pio": bel[2]}
    for bel, data in sorted(metadata.items()):
        if chip.info.family.startswith("MachXO"):
            bank, function, dqs, io_grouping = data
        else:
            bank, function, dqs = data
        meta = {
            "col": bel[0],
            "row": bel[1],
            "pio": bel[2],
            "bank": bank
        }
        if function != "-" and len(function)>0:
            meta["function"] = function
        if dqs != "-" and len(dqs)>0:
            meta["dqs"] = dqs

        if chip.info.family.startswith("MachXO"):
            # Since "+" is used, "-" means "minus" presumably, as opposed to
            # "not applicable".
            meta["io_grouping"] = io_grouping

        json_data["pio_metadata"].append(meta)
    with args.outfile as jsonf:
        jsonf.write(json.dumps(json_data, sort_keys=True, indent=4, separators=(',', ': ')))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Store pinout information into iodb.json.")
    parser.add_argument('device', type=str,
                        help="Device for which to generate iodb.json (family autodetected).")
    parser.add_argument('infile', type=argparse.FileType('r'),
                        help="Input pinout CSV file from Lattice.")
    parser.add_argument('outfile', type=argparse.FileType('w'),
                        help="Output json file (iodb.json in the database).")
    args = parser.parse_args()

    main(args)
