#!/usr/bin/env python3
"""
This script reads the output from Lattice's bstool in "test" mode, which should be invoked thus:

```
bstool -t bitstream.bit > bitstream.test
```

and from it obtains a list of tiles with the following information:
    - Tile name (with position encoded in the name)
    - Tile type
    - Frame and bit offset
    - Bitstream size in bits ("rows") and frames ("cols")
    - Sites contained within the tile, and their nominal location
and creates a JSON file as output
"""

import sys, re
import json, argparse

tile_re = re.compile(
    r'^Tile\s+([A-Z0-9a-z_/]+)\s+\((\d+), (\d+)\)\s+bitmap offset\s+\((\d+), (\d+)\)\s+\<([A-Z0-9a-z_/]+)>\s*$')

site_re = re.compile(
    r'^\s+([A-Z0-9_]+) \((-?\d+), (-?\d+)\)')

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('infile', type=argparse.FileType('r'),
                    help="input file from bstool")
parser.add_argument('outfile', type=argparse.FileType('w'),
                    help="output JSON file")

def main(argv):
    args = parser.parse_args(argv[1:])
    tiles = {}
    current_tile = None
    for line in args.infile:
        tile_m = tile_re.match(line)
        if tile_m:
            name = tile_m.group(6)
            current_tile = {
                "type": tile_m.group(1),
                "start_bit": int(tile_m.group(4)),
                "start_frame": int(tile_m.group(5)),
                "rows": int(tile_m.group(2)),
                "cols": int(tile_m.group(3)),
                "sites": []
            }
            identifier = name + ":" + tile_m.group(1)
            assert identifier not in tiles
            tiles[identifier] = current_tile
        else:
            site_m = site_re.match(line)
            if site_m and current_tile is not None:
                current_tile["sites"].append({
                    "name": site_m.group(1),
                    "pos_row": site_m.group(2),
                    "pos_col": site_m.group(3)
                })
    json.dump(tiles, args.outfile, sort_keys=True, indent=4)


if __name__ == "__main__":
    main(sys.argv)
