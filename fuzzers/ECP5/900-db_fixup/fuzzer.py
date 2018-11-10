import dbfixup
import pytrellis

device = "LFE5UM5G-45F"


def main():
    pytrellis.load_database("../../../database")
    chip = pytrellis.Chip("LFE5UM5G-45F")
    tiletypes = set()
    for tile in chip.get_all_tiles():
        tiletypes.add(tile.info.type)

    for tiletype in sorted(tiletypes):
        dbfixup.dbfixup("ECP5", device, tiletype)


if __name__ == "__main__":
    main()
