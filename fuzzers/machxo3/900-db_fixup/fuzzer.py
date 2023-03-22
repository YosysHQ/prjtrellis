import dbfixup
import pytrellis

devices = [ "LCMXO3LF-1300E", "LCMXO3LF-2100C", "LCMXO3LF-4300C", "LCMXO3LF-6900C", "LCMXO3LF-9400C" ]


def fix_device(device):
    chip = pytrellis.Chip(device)
    tiletypes = set()
    for tile in chip.get_all_tiles():
        tiletypes.add(tile.info.type)

    for tiletype in sorted(tiletypes):
        dbfixup.dbfixup("MachXO3", device, tiletype)


def main():
    pytrellis.load_database("../../../database")
    for dev in devices:
        fix_device(dev)

if __name__ == "__main__":
    main()
