import pytrellis

# BOOTADDR is bit 23..16 of the address for the next image to boot
# when PROGRAMN is asserted.
# This Config word is as far as I can tell never generated by
# Diamond itself, but instead by the Deployment tool
# For this reason, I have manually "fuzzed" the info for it.
# The name is arbitrarily chosen.


def main():
    pytrellis.load_database("../../../database")

    config = [
        (46, 1, 0),
        (48, 1, 0),
        (50, 1, 0),
        (54, 1, 0),
        (56, 1, 0),
        (58, 1, 0),
        (60, 1, 0),
        (62, 1, 0),
    ]

    tile = pytrellis.get_tile_bitdata(
        pytrellis.TileLocator("ECP5", "LFE5U-25F", "EFB1_PICB1"))
    wsb = pytrellis.WordSettingBits()
    wsb.name = "BOOTADDR"

    for bframe, bbit, inv in config:
        bg = pytrellis.BitGroup()
        cb = pytrellis.ConfigBit()
        cb.frame = bframe
        cb.bit = bbit
        cb.inv = inv
        bg.bits.add(cb)
        wsb.bits.append(bg)
        wsb.defval.append(False)

    tile.add_setting_word(wsb)
    tile.save()


if __name__ == "__main__":
    main()
