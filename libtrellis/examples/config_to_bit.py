#!/usr/bin/env python3
"""
This example uses PyTrellis to convert the text-config from bit_to_config.py back to a bitstream
"""
import pytrellis
import sys

pytrellis.load_database("../../database")

def get_next_nonblank(f):
    while True:
        line = f.readline()
        if line == "":
            return None
        if '#' in line:
            line = line[:line.index('#')]
        if len(line.strip()) == 0:
            continue
        return line.rstrip('\n')


def main(argv):
    block_hdr = ""
    block_content = ""
    chip = None
    seen_tiles = set()

    def finalise_last_block():
        if block_hdr.startswith(".tile"):
            tile_name = block_hdr.split(" ")[1]
            chip.tiles[tile_name].read_config(block_content)
            seen_tiles.add(tile_name)

    with open(argv[1], 'r') as cfg:
        while True:
            l = get_next_nonblank(cfg)
            if l is None:
                break
            if l.startswith('.'):
                finalise_last_block()
                block_hdr = l
                block_content = ""
                if l.startswith(".device "):
                    chip = pytrellis.Chip(l.split(" ")[1])
                elif l.startswith(".comment "):
                    chip.metadata.append(l.split(" ", 1)[1])
                elif l.startswith(".tile "):
                    pass
                else:
                    assert False, "unrecognised dot-statement {}".format(l.split(" ")[0])
            else:
                block_content += l
                block_content += "\n"
        finalise_last_block()

    # Init unseen tiles with the default config
    for tile in chip.get_all_tiles():
        if tile.info.name not in seen_tiles:
            tile.read_config("")

    bs = pytrellis.Bitstream.serialise_chip(chip)
    bs.write_bit(argv[2])


if __name__ == "__main__":
    main(sys.argv)
