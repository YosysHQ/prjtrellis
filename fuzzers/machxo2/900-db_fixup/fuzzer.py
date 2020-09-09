import dbfixup
import pytrellis

device = "LCMXO2-1200HC"


def main():
    pytrellis.load_database("../../../database")
    chip = pytrellis.Chip("LCMXO2-1200HC")
    tiletypes = set()
    for tile in chip.get_all_tiles():
        tiletypes.add(tile.info.type)

    for tiletype in sorted(tiletypes):
        dbfixup.dbfixup("MachXO2", device, tiletype)


if __name__ == "__main__":
    main()
