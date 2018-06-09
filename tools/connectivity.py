#!/usr/bin/env python3
import pytrellis
import nets
import tiles
import database

# Interactive connectivity explorer
# All netnames here are canonical


# Key
# <-- net driven by mux
# <== net driven by fixed conn
# --> net drives mux input
# ==> net drives net by fixed conn

def main():
    pytrellis.load_database(database.get_db_root())
    c = pytrellis.Chip("LFE5U-45F")
    chip_size = (c.get_max_row(), c.get_max_col())
    # Get fan-in to a net
    # Returns (source, configurable, loc)
    def get_fanin(net):
        drivers = []
        npos = tiles.pos_from_name(net)
        for tile in c.get_all_tiles():
            tinf = tile.info
            tname = tinf.name
            pos = tiles.pos_from_name(tname)
            if abs(pos[0] - npos[0]) >= 10 or abs(pos[1] - npos[1]) >= 10:
                continue
            if net.startswith("G_"):
                tnet = net
            else:
                tnet = nets.normalise_name(chip_size, tname, net)
            tdb = pytrellis.get_tile_bitdata(pytrellis.TileLocator(c.info.family, c.info.name, tinf.type))
            try:
                mux = tdb.get_mux_data_for_sink(tnet)
                for src in mux.get_sources():
                    drivers.append((nets.canonicalise_name(chip_size, tname, src), True, tname))
            except IndexError:
                pass
            for fc in tdb.get_fixed_conns():
                if fc.sink == tnet:
                    drivers.append((nets.canonicalise_name(chip_size, tname, fc.source), False, tname))
        return drivers

    # Get fan-out of a net
    # Returns (dest, configurable, loc)
    def get_fanout(net):
        drivers = []
        npos = tiles.pos_from_name(net)
        for tile in c.get_all_tiles():
            tinf = tile.info
            tname = tinf.name
            pos = tiles.pos_from_name(tname)
            if abs(pos[0] - npos[0]) >= 12 or abs(pos[1] - npos[1]) >= 12:
                continue
            if net.startswith("G_"):
                tnet = net
            else:
                tnet = nets.normalise_name(chip_size, tname, net)
            tdb = pytrellis.get_tile_bitdata(pytrellis.TileLocator(c.info.family, c.info.name, tinf.type))
            for sink in tdb.get_sinks():
                mux = tdb.get_mux_data_for_sink(sink)
                if tnet in mux.arcs:
                    drivers.append((nets.canonicalise_name(chip_size, tname, sink), True, tname))
            for fc in tdb.get_fixed_conns():
                if fc.source == tnet:
                    drivers.append((nets.canonicalise_name(chip_size, tname, fc.sink), False, tname))
        return drivers


    hist_buf = []
    while True:
        net = input("> ")
        if net == "quit":
            return
        if net.isdigit():
            idx = int(net)
            if idx > len(hist_buf):
                print("Invalid index into last result")
                continue
            else:
                net = hist_buf[idx]
        hist_buf = []
        fi = get_fanin(net)
        for drv in fi:
            finet, conf, tile = drv
            if finet is None: continue
            arrow = "<--" if conf else "<=="
            print("[{:3d}]  {} {} {:25s} [in {}]".format(len(hist_buf), net, arrow, finet, tile))
            hist_buf.append(finet)
        print()
        fo = get_fanout(net)
        for src in fo:
            fonet, conf, tile = src
            if fonet is None: continue
            arrow = "-->" if conf else "==>"
            print("[{:3d}]  {} {} {:25s} [in {}]".format(len(hist_buf), net, arrow, fonet, tile))
            hist_buf.append(fonet)

if __name__ == "__main__":
    main()
