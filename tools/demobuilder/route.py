import prjtellis
import tiles
import nets

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
            if wire.startswith("G_"):
                return [] #NYI
            npos = tiles.pos_from_name(wire)
            for tile in self.chip.get_all_tiles():
                tinf = tile.info
                tname = tinf.name
                pos = tiles.pos_from_name(tname)
                if abs(pos[0] - npos[0]) >= 12 or abs(pos[1] - npos[1]) >= 12:
                    continue
                if wire.startswith("G_"):
                    twire = wire
                else:
                    twire = nets.normalise_name(self.chip_size, tname, wire)
                tdb = pytrellis.get_tile_bitdata(pytrellis.TileLocator(self.chip.info.family, self.chip.info.name, tinf.type))
                for sink in tdb.get_sinks():
                    mux = tdb.get_mux_data_for_sink(sink)
                    if twire in mux.arcs:
                        drivers.append((nets.canonicalise_name(self.chip_size, tname, sink), True, tname))
                for fc in tdb.get_fixed_conns():
                    if fc.source == twire:
                        drivers.append((nets.canonicalise_name(self.chip_size, tname, fc.sink), False, tname))
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
            self.net_to_wire[net].insert(dest_wire)
        else:
            self.net_to_wire[net] = set(dest_wire)
        if configurable and not exists:
            src_wirename = nets.normalise_name(self.chip_size, tile, uphill_wire)
            sink_wirename = nets.normalise_name(self.chip_size, tile, dest_wire)
            config[tile].add_arc(sink_wirename, src_wirename)

    # Bind a net to a wire (used for port connections)
    def bind_net_to_port(self, net, port_wire):
        assert (port_wire not in self.wire_to_net) or (self.wire_to_net[port_wire] == net)
        self.wire_to_net[port_wire] = net
        if net in self.net_to_wire:
            self.net_to_wire[net].insert(port_wire)
        else:
            self.net_to_wire[net] = set(port_wire)

