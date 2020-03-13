#!/usr/bin/env python3
"""
For each family and device, obtain a tilegrid and save it in the database
"""

import os
from os import path
import shutil

import extract_tilegrid
import diamond
import database



def main():
    shutil.rmtree("work_tilegrid", ignore_errors=True)
    os.mkdir("work_tilegrid")
    shutil.copy(path.join(database.get_trellis_root(), "minitests", "wire", "wire.v"), "work_tilegrid/wire.v")

    devices = database.get_devices()
    for family in sorted(devices["families"].keys()):
        for device in sorted(devices["families"][family]["devices"].keys()):
            if devices["families"][family]["devices"][device]["fuzz"]:
                diamond.run(device, "work_tilegrid/wire.v")
                output_file = path.join(database.get_db_subdir(family, device), "tilegrid.json")
                if family in ["MachXO2"]:
                    extract_tilegrid.main(["extract_tilegrid", "-m", "work_tilegrid/wire.tmp/output.test", output_file])
                else:
                    extract_tilegrid.main(["extract_tilegrid", "work_tilegrid/wire.tmp/output.test", output_file])


if __name__ == "__main__":
    main()
