import dbfixup
import pytrellis

devices = [ "LCMXO2-256", "LCMXO2-640", "LCMXO2-1200", "LCMXO2-2000", "LCMXO2-4000", "LCMXO2-7000" ]


def fix_device(device):
    chip = pytrellis.Chip(device)
    tiletypes = set()
    for tile in chip.get_all_tiles():
        tiletypes.add(tile.info.type)

    for tiletype in sorted(tiletypes):
        dbfixup.dbfixup("MachXO2", device, tiletype)


def main():
    pytrellis.load_database("../../../database")
    for dev in devices:
        fix_device(dev)

if __name__ == "__main__":
    main()
