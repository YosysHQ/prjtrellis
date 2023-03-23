import dbcopy
import pytrellis

# Then copy the BRANCH info from CIB_PIC_T0 back to the other tiles.
shared_tiles = ["CIB_PIC_T0", "CIB_PIC_T_DUMMY", "CIB_CFG0", "CIB_CFG1", "CIB_CFG2", "CIB_CFG3"]

def copy(tile):
    srcdb = pytrellis.get_tile_bitdata(
        pytrellis.TileLocator("MachXO3", "LCMXO3LF-6900C", "CIB_PIC_T0"))
    dstdb = pytrellis.get_tile_bitdata(
        pytrellis.TileLocator("MachXO3", "LCMXO3LF-6900C", tile))

    sinks = srcdb.get_sinks()
    for sink in sinks:
        mux = srcdb.get_mux_data_for_sink(sink)
        for src in mux.get_sources():
            dstdb.add_mux_arc(mux.arcs[src])

    cwords = srcdb.get_settings_words()
    for cword in cwords:
        wd = srcdb.get_data_for_setword(cword)
        dstdb.add_setting_word(wd)

    cenums = srcdb.get_settings_enums()
    for cenum in cenums:
        ed = srcdb.get_data_for_enum(cenum)
        dstdb.add_setting_enum(ed)

    fcs = srcdb.get_fixed_conns()
    for conn in fcs:
        dstdb.add_fixed_conn(conn)


def main():
    pytrellis.load_database("../../../database")

    for tile in shared_tiles:
        copy(tile)

if __name__ == "__main__":
    main()

