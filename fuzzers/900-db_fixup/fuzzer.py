import dbfixup
import pytrellis

device = "LFE5U-45F"


def main():
    pytrellis.load_database("../../database")
    chip = pytrellis.Chip("LFE5U-45F")
    tiletypes = set()
    for tile in chip.get_all_tiles():
        tiletypes.add(tile.info.type)

    for tiletype in sorted(tiletypes):
        dbfixup.dbfixup("ECP5", device, tiletype)


if __name__ == "__main__":
    main()
