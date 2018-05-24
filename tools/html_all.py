#!/usr/bin/env python3
"""
Project Trellis Master HTML Generation Script

Usage:
html_all.py <output_folder>
"""

import os, sys, time
from os import path
from string import Template
import argparse
import database
import devices
import html_tilegrid
import html_bits

trellis_docs_index = """
<html>
<head>
<title>Project Trellis HTML Documentation</title>
</head>
<body>
<h1>Project Trellis HTML Documentation</h1>
<p>Project Trellis is a project to document the ECP5 bitstream and internal architecture.</p>
<p>This repository contains HTML documentation automatically generated from the
<a href="https://github.com/SymbiFlow/prjtrellis">Project Trellis</a> database. The equivalent
machine-readable data is located in <a href="https://github.com/SymbiFlow/prjtrellis-db">prjtrellis-db.<a/>
Currently only tilemap data is published. More information on routing and bitstream will be published in the future.
</p>

<p>More human-readable documentation on the ECP5 architecture and the Project Trellis methodology can be found
on the <a href="http://prjtrellis.readthedocs.io/en/latest/">Read the Docs</a> site.</p>

<p>This HTML documentation was generated at ${datetime} from prjtrellis-db commit
<a href="https://github.com/SymbiFlow/prjtrellis-db/tree/${commit}">${commit}</a>.</p>
<hr/>
$docs_toc
<hr/>
<p>Licensed under a very permissive <a href="COPYING">CC0 1.0 Universal</a> license.</p>
</body>
</html>
"""

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('fld', type=str,
                    help="output folder")


def generate_device_docs(family, device, folder):
    html_tilegrid.main(["html_tilegrid", family, device, path.join(folder, "index.html")])


def generate_tile_docs(family, device, tile, folder):
    html_bits.main(["html_bits", family, device, tile, path.join(folder, "{}.html".format(tile))])


# TODO find a better way of specifying tiles, or just go for all of them
tiles = {
    ("ECP5", "LFE5U-25F"): ["PLC2", "TAP_DRIVE", "TAP_DRIVE_CIB", "CIB", "CIB_LR", "MIB_EBR0"],
    ("ECP5", "LFE5U-45F"): ["EBR_SPINE_UL1", "EBR_SPINE_UL0", "EBR_SPINE_UR0", "EBR_SPINE_UR1", "EBR_SPINE_LL1",
                            "EBR_SPINE_LL0", "EBR_SPINE_LR0", "EBR_SPINE_LR1"]
}


def main(argv):
    args = parser.parse_args(argv[1:])
    if not path.exists(args.fld):
        os.mkdir(args.fld)
    commit_hash = database.get_db_commit()
    build_dt = time.strftime('%Y-%m-%d %H:%M:%S')
    docs_toc = ""
    for fam, fam_data in sorted(devices.families.items()):
        fdir = path.join(args.fld, fam)
        if not path.exists(fdir):
            os.mkdir(fdir)
        thdir = path.join(fdir, "tilehtml")
        if not path.exists(thdir):
            os.mkdir(thdir)
        docs_toc += "<h3>{} Family</h3>".format(fam)
        docs_toc += "<ul>"
        for dev in fam_data["devices"]:
            ddir = path.join(fdir, dev)
            if not path.exists(ddir):
                os.mkdir(ddir)
            generate_device_docs(fam, dev, ddir)
            if (fam, dev) in tiles:
                for tile in tiles[fam, dev]:
                    generate_tile_docs(fam, dev, tile, thdir)
            docs_toc += '<li><a href="{}">{} Documentation</a></li>'.format(
                '{}/{}/index.html'.format(fam, dev),
                dev
            )

        docs_toc += "</ul>"

    index_html = Template(trellis_docs_index).substitute(
        datetime=build_dt,
        commit=commit_hash,
        docs_toc=docs_toc
    )
    with open(path.join(args.fld, "index.html"), 'w') as f:
        f.write(index_html)


if __name__ == "__main__":
    main(sys.argv)
