import dbfixup
import pytrellis

devices = [ "LCMXO3D-4300HC", "LCMXO3D-9400HC" ]


def fix_device(device):
    chip = pytrellis.Chip(device)
    tiletypes = set()
    for tile in chip.get_all_tiles():
        tiletypes.add(tile.info.type)

    for tiletype in sorted(tiletypes):
        dbfixup.dbfixup("MachXO3D", device, tiletype)


def main():
    pytrellis.load_database("../../../database")
    for dev in devices:
        fix_device(dev)

if __name__ == "__main__":
    main()
