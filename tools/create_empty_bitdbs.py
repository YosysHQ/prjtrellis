#!/usr/bin/env python3
"""
For each family, read the tilegrid for all devices and create empty bit databases for all tiles, if they don't exist
already
"""

import os
from os import path
import database
import tiles

def main():
    devices = database.get_devices()
    for fam, famdata in sorted(devices["families"].items()):
        tdroot = path.join(database.get_db_root(), fam, "tiledata")
        if not path.exists(tdroot):
            os.mkdir(tdroot)
        for device in sorted(famdata["devices"].keys()):
            if famdata["devices"][device]["fuzz"]:
                tilegrid = database.get_tilegrid(fam, device)
                for tilename in sorted(tilegrid.keys()):
                    tile = tiles.type_from_fullname(tilename)
                    tile_dir = path.join(tdroot, tile)
                    if not path.exists(tile_dir):
                        os.mkdir(tile_dir)
                    tile_db = path.join(tile_dir, "bits.db")
                    if not path.exists(tile_db):
                        with open(tile_db, 'w') as f:
                            f.write('\n')


if __name__ == "__main__":
    main()
