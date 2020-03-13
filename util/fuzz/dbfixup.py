import pytrellis

"""
Database fix utility

Run at the end of fuzzing to "finalise" the database and remove problems that may occur during fuzzing.

The remaining functions can be called in other fuzzers as necessary.
"""


def dbfixup(family, device, tiletype):
    db = pytrellis.get_tile_bitdata(
        pytrellis.TileLocator(family, device, tiletype))

    fc = db.get_fixed_conns()
    # Where a wire is driven by both a mux and fixed connections, replace those fixed connections
    # with a mux arc with no config bits
    for mux in db.get_sinks():
        deleteFc = False
        for conn in fc:
            if conn.sink == mux:
                ad = pytrellis.ArcData()
                ad.source = conn.source
                ad.sink = conn.sink
                db.add_mux_arc(ad)
                deleteFc = True
        if deleteFc:
            db.remove_fixed_sink(mux)
    db.save()


def remove_enum_bits(family, device, tiletype, lowerright, upperleft=(0, 0)):
    """
    Remove bits from enumerations in a given tile that actually belong
    to routing bits. This can happen when e.g. routing is required for Diamond
    to set certain bits in the output, as is the case for fuzzing I/O enums
    in PIC_L0 and PIC_R0.

    Bounds are (0,0)-based. Upperleft is inclusive, lowerright is exclusive.
    """
    def in_bounding_box(bit):
        (x, y) = (bit.frame, bit.bit)

        if upperleft[0] > x or upperleft[1] > y:
            return False

        if lowerright[0] <= x or lowerright[1] <= y:
            return False

        return True

    db = pytrellis.get_tile_bitdata(
        pytrellis.TileLocator(family, device, tiletype))

    for enum in db.get_settings_enums():
        fixed_enum = pytrellis.EnumSettingBits()

        for option in db.get_data_for_enum(enum).options:
            key = option.key()
            fixed_bg = pytrellis.BitGroup()

            for bit in option.data().bits:
                if in_bounding_box(bit):
                    fixed_bg.bits.add(bit)

            fixed_enum.options[key] = fixed_bg

        fixed_enum.name = db.get_data_for_enum(enum).name
        fixed_enum.defval = db.get_data_for_enum(enum).defval

        db.remove_setting_enum(enum)
        db.add_setting_enum(fixed_enum)
    db.save()
