# Pastebin J2L5zfiT
#!/usr/bin/env python3
import sys
import json

# (X, Y, Z)
def get_bel(pin):
    assert pin[0] == "P"
    edge = pin[1]
    pos = int(pin[2:-1])
    pio = pin[-1]
    if edge == "T":
        return (pos, 0, pio)
    elif edge == "B":
        return (pos, max_row, pio)
    elif edge == "L":
        return (0, pos, pio)
    elif edge == "R":
        return (max_col, pos, pio)
    else:
        assert False

def main(argv):
    global max_row, max_col

    if "45" in argv[1]:
        max_row = 71
        max_col = 90
    elif "25" in argv[1]:
        max_row = 50
        max_col = 72
    elif "85" in argv[1]:
        max_row = 95
        max_col = 126
    
    metadata = dict()
    package_data = dict()
    package_indicies = None
    found_header = False
    with open(argv[1], 'r') as csvf:
        for line in csvf:
            trline = line.strip()
            splitline = trline.split(",")
            if len(splitline) < 8:
                continue
            if len(splitline[0].strip()) == 0:
                continue
            if splitline[0] == "PAD":
                # is header
                found_header = True
                package_indicies = splitline[7:]
                for pkg in package_indicies:
                    package_data[pkg] = {}
            elif found_header:
                if splitline[1][0] != "P" or splitline[1].startswith("PROGRAM"):
                    continue
                bel = get_bel(splitline[1])
                bank = int(splitline[2])
                function = splitline[3]
                dqs = splitline[6]
                metadata[bel] = bank, function, dqs
                for i in range(len(package_indicies)):
                    if splitline[7+i] == "-":
                        continue
                    package_data[package_indicies[i]][splitline[7+i]] = bel
    json_data = {"packages": {}, "pio_metadata": []}
    for pkg, pins in package_data.items():
        json_data["packages"][pkg] = {}
        for pin, bel in pins.items():
            json_data["packages"][pkg][pin] = {"col": bel[0], "row": bel[1], "pio": bel[2]}
    for bel, data in sorted(metadata.items()):
        bank, function, dqs = data
        meta = {
            "col": bel[0],
            "row": bel[1],
            "pio": bel[2],
            "bank": bank
        }
        if function != "-":
            meta["function"] = function
        if dqs != "-":
            meta["dqs"] = dqs
        json_data["pio_metadata"].append(meta)
    with open(argv[2], 'w') as jsonf:
        jsonf.write(json.dumps(json_data, sort_keys=True, indent=4, separators=(',', ': ')))


if __name__ == "__main__":
    main(sys.argv)
