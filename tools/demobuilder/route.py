#!/usr/bin/env python3
import pytrellis
import tiles
import nets
import database
import heapq


# Simple automatic router
class Autorouter:
    def __init__(self, chip):
        self.chip = chip
        self.chip_size = (self.chip.get_max_row(), self.chip.get_max_col())
        self.dh_arc_cache = {}
        self.net_to_wire = {}
        self.wire_to_net = {}

    # Get arcs downhill of a wire
    # Returns list [(dest, configurable, loc), ...]
    def get_arcs_downhill(self, wire):
        if wire in self.dh_arc_cache:
            return self.dh_arc_cache[wire]
        else:
            drivers = []
            try:
                npos = tiles.pos_from_name(wire)
            except AssertionError:
                return []
            wname = wire.split("_", 1)[1]
            hspan = 0
            vspan = 0
            if wname.startswith("H") and wname[1:3].isdigit():
                hspan = int(wname[1:3])
            if wname.startswith("V") and wname[1:3].isdigit():
                vspan = int(wname[1:3])
            positions = {(npos[0], npos[1]), (npos[0] + vspan, npos[1]), (npos[0] - vspan, npos[1]),
                         (npos[0], npos[1] + hspan), (npos[0], npos[1] - hspan)}
            for pos in positions:
                for tile in self.chip.get_tiles_by_position(pos[0], pos[1]):
                    tinf = tile.info
                    tname = tinf.name
                    if tname.startswith("TAP"):
                        continue
                    pos = tiles.pos_from_name(tname)

                    if abs(pos[0] - npos[0]) not in (vspan, 0) or abs(pos[1] - npos[1]) not in (hspan, 0):
                        continue
                    if wire.startswith("G_"):
                        twire = wire
                    else:
                        twire = nets.normalise_name(self.chip_size, tname, wire)

                    tdb = pytrellis.get_tile_bitdata(
                        pytrellis.TileLocator(self.chip.info.family, self.chip.info.name, tinf.type))
                    downhill = tdb.get_downhill_wires(twire)
                    for sink in downhill:
                        nn = nets.canonicalise_name(self.chip_size, tname, sink.first)
                        if nn is not None:
                            drivers.append((nn, sink.second, tname))
            self.dh_arc_cache[wire] = drivers
            return drivers

    # Enable an Arc
    def bind_arc(self, net, uphill_wire, arc, config):
        dest_wire, configurable, tile = arc
        assert (dest_wire not in self.wire_to_net) or (self.wire_to_net[dest_wire] == net)
        self.wire_to_net[dest_wire] = net
        exists = False
        if net in self.net_to_wire:
            exists = dest_wire in self.net_to_wire[net]
            self.net_to_wire[net].add(dest_wire)
        else:
            self.net_to_wire[net] = {dest_wire}
        if configurable and not exists:
            src_wirename = nets.normalise_name(self.chip_size, tile, uphill_wire)
            sink_wirename = nets.normalise_name(self.chip_size, tile, dest_wire)
            config[tile].add_arc(sink_wirename, src_wirename)

    # Bind a net to a wire (used for port connections)
    def bind_net_to_port(self, net, port_wire):
        assert (port_wire not in self.wire_to_net) or (self.wire_to_net[port_wire] == net)
        self.wire_to_net[port_wire] = net
        if net in self.net_to_wire:
            self.net_to_wire[net].add(port_wire)
        else:
            self.net_to_wire[net] = {port_wire}

    # Route a net to a wire
    def route_net_to_wire(self, net, wire, config):
        print("     Routing net '{}' to wire/pin '{}'...".format(net, wire))
        dest_pos = tiles.pos_from_name(wire)
        def get_score(x_wire):
            pos = tiles.pos_from_name(x_wire)
            score = abs(pos[0] - dest_pos[0]) + abs(pos[1] - dest_pos[1])
            x_wname = x_wire.split("_", 1)[1]
            if x_wname[1:3].isdigit() and score > 3:
                score -= int(x_wname[1:3])
            return score

        assert net in self.net_to_wire
        bfs_queue = [(get_score(x), x) for x in sorted(self.net_to_wire[net])]
        heapq.heapify(bfs_queue)

        seen_wires = set()
        routed = False
        backtrace = {}  # map wire -> (source, arc)

        while not routed and len(bfs_queue) > 0:
            score, curr_wire = heapq.heappop(bfs_queue)
            #print(curr_wire)
            arcs = self.get_arcs_downhill(curr_wire)
            for arc in arcs:
                dest, cfg, loc = arc
                if dest == wire:
                    backtrace[dest] = (curr_wire, arc)
                    routed = True
                    break
                elif dest not in seen_wires:
                    if dest in self.wire_to_net and self.wire_to_net[dest] != net:
                        continue
                    backtrace[dest] = (curr_wire, arc)
                    heapq.heappush(bfs_queue, (get_score(dest), dest))
                    seen_wires.add(dest)

        if routed:
            cursor = wire
            while cursor in backtrace:
                cursor, arc = backtrace[cursor]
                self.bind_arc(net, cursor, arc, config)
        else:
            assert False, "failed to route net {} to wire {}".format(net, wire)


def main():
    pytrellis.load_database(database.get_db_root())
    chip = pytrellis.Chip("LFE5U-45F")
    rt = Autorouter(chip)
    config = {_.info.name: pytrellis.TileConfig() for _ in chip.get_all_tiles()}
    rt.bind_net_to_port("x", "R15C10_Q0")
    rt.route_net_to_wire("x", "R15C50_A0", config)
    for tile, tcfg in sorted(config.items()):
        cfgtext = tcfg.to_string()
        if len(cfgtext.strip()) > 0:
            print(".tile {}".format(tile))
            print(cfgtext)


if __name__ == "__main__":
    main()
