import pytrellis

"""
Database copy utilities

This is used where there are several tiles with different types but the same or similar bit databases - such as all the
CIB tiles, some IO tiles, etc.
"""


def dbcopy(family, device, source, dest, copy_muxes=True, copy_words=True, copy_enums=True, copy_conns=True):
    """
    Copy the bit database from one tile type to another

    :param family: database family
    :param device: database device
    :param source: tiletype to copy from
    :param dest: tiletype to copy to
    :param copy_muxes: include muxes in copy
    :param copy_words: include settings words in copy
    :param copy_enums: include settings enums in copy
    :param copy_conns: include fixed connections in copy
    """
    srcdb = pytrellis.get_tile_bitdata(
        pytrellis.TileLocator(family, device, source))
    dstdb = pytrellis.get_tile_bitdata(
        pytrellis.TileLocator(family, device, dest))

    if copy_muxes:
        sinks = srcdb.get_sinks()
        for sink in sinks:
            mux = srcdb.get_mux_data_for_sink(sink)
            for src in mux.get_sources():
                dstdb.add_mux_arc(mux.arcs[src])

    if copy_words:
        cwords = srcdb.get_settings_words()
        for cword in cwords:
            wd = srcdb.get_data_for_setword(cword)
            dstdb.add_setting_word(wd)

    if copy_enums:
        cenums = srcdb.get_settings_enums()
        for cenum in cenums:
            ed = srcdb.get_data_for_enum(cenum)
            dstdb.add_setting_enum(ed)

    if copy_conns:
        fcs = srcdb.get_fixed_conns()
        for conn in fcs:
            dstdb.add_fixed_conn(conn)
