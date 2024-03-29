#!/usr/bin/env python3
import sys
import pytrellis
import nets
import tiles
import database
if sys.platform in ("win32"):
    import pyreadline.rlmain
import readline
import re

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
    row_bias = c.info.row_bias
    col_bias = c.info.col_bias

    # Get fan-in to a net
    # Returns (source, configurable, loc)
    def get_fanin(net):
        drivers = []
        npos = tiles.pos_from_name(net, chip_size, row_bias, col_bias)
        for tile in c.get_all_tiles():
            tinf = tile.info
            tname = tinf.name
            pos = tiles.pos_from_name(tname, chip_size, row_bias, col_bias)
            if abs(pos[0] - npos[0]) >= 10 or abs(pos[1] - npos[1]) >= 10:
                continue
            if net.startswith("G_"):
                tnet = net
            else:
                tnet = nets.normalise_name(chip_size, tname, net, c.info.family)
            tdb = pytrellis.get_tile_bitdata(pytrellis.TileLocator(c.info.family, c.info.name, tinf.type))
            try:
                mux = tdb.get_mux_data_for_sink(tnet)
                for src in mux.get_sources():
                    drivers.append((nets.canonicalise_name(chip_size, tname, src, row_bias, col_bias), True, tname))
            except IndexError:
                pass
            for fc in tdb.get_fixed_conns():
                if fc.sink == tnet:
                    drivers.append((nets.canonicalise_name(chip_size, tname, fc.source, row_bias, col_bias), False, tname))
        return drivers

    # Get fan-out of a net
    # Returns (dest, configurable, loc)
    def get_fanout(net):
        drivers = []
        npos = tiles.pos_from_name(net, chip_size, row_bias, col_bias)
        for tile in c.get_all_tiles():
            tinf = tile.info
            tname = tinf.name
            pos = tiles.pos_from_name(tname, chip_size, row_bias, col_bias)
            if abs(pos[0] - npos[0]) >= 12 or abs(pos[1] - npos[1]) >= 12:
                continue
            if net.startswith("G_"):
                tnet = net
            else:
                tnet = nets.normalise_name(chip_size, tname, net, c.info.family)
            tdb = pytrellis.get_tile_bitdata(pytrellis.TileLocator(c.info.family, c.info.name, tinf.type))
            for sink in tdb.get_sinks():
                mux = tdb.get_mux_data_for_sink(sink)
                if tnet in mux.arcs:
                    drivers.append((nets.canonicalise_name(chip_size, tname, sink, row_bias, col_bias), True, tname))
            for fc in tdb.get_fixed_conns():
                if fc.source == tnet:
                    drivers.append((nets.canonicalise_name(chip_size, tname, fc.sink, row_bias, col_bias), False, tname))
        return drivers


    # Get all nets at a location
    net_tile_cache = {}
    non_tile_re = re.compile(r"^([NS]\d+)?([EW]\d+)?[GLR]?_.*")

    def get_nets_at(loc):
        if loc in net_tile_cache:
            return net_tile_cache[loc]
        row, col = loc
        nets = set()
        for tile in c.get_tiles_by_position(row, col):
            tinf = tile.info
            tdb = pytrellis.get_tile_bitdata(pytrellis.TileLocator(c.info.family, c.info.name, tinf.type))
            for sink in tdb.get_sinks():
                if not non_tile_re.match(sink):
                    nets.add(sink)
                mux = tdb.get_mux_data_for_sink(sink)
                for src in mux.get_sources():
                    if not non_tile_re.match(src):
                        nets.add(src)
            for fc in tdb.get_fixed_conns():
                if not non_tile_re.match(fc.sink):
                    nets.add(fc.sink)
                if not non_tile_re.match(fc.source):
                    nets.add(fc.source)
        nets = list(sorted((["R{}C{}_{}".format(row, col, _) for _ in nets])))
        net_tile_cache[loc] = nets
        return nets

    tile_net_re = re.compile(r"^R\d+C\d+_.*")
    def completer(str, idx):
        if not tile_net_re.match(str):
            return None
        loc = tiles.pos_from_name(str, chip_size, row_bias, col_bias)
        nets = get_nets_at(loc)
        for n in nets:
            if n.startswith(str):
                if idx > 0:
                    idx -= 1
                else:
                    return n
        return None

    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)

    hist_buf = []
    while True:
        net = input("> ")
        if net.strip() == "":
            continue
        if net == "quit":
            return
        if net.isdigit():
            idx = int(net)
            if idx >= len(hist_buf):
                print("Invalid index into last result")
                continue
            else:
                net = hist_buf[idx]
        if not tile_net_re.match(net):
            print("Bad netname, expected RyCx_...")
            continue
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
