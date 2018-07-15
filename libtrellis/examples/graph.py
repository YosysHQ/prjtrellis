#!/usr/bin/env python3
"""
Testing the routing graph generator
"""
import pytrellis
import sys

pytrellis.load_database("../../database")
chip = pytrellis.Chip("LFE5U-45F")
rg = chip.get_routing_graph()
tile = rg.tiles[pytrellis.Location(9, 71)]
for wire in tile.wires:
    print("Wire {}:".format(rg.to_str(wire.key())))
    for dh in wire.data().downhill:
        arc = rg.tiles[dh.loc].arcs[dh.id]
        print("     --> R{}C{}_{}".format(arc.sink.loc.y, arc.sink.loc.x, rg.to_str(arc.sink.id)))
    for bdh in wire.data().belsDownhill:
        print("     ->| R{}C{}_{}.{}".format(bdh.bel.loc.y, bdh.bel.loc.x, rg.to_str(bdh.bel.id), rg.to_str(bdh.pin)))
    print()
    for uh in wire.data().uphill:
        arc = rg.tiles[uh.loc].arcs[uh.id]
        print("     <-- R{}C{}_{}".format(arc.source.loc.y, arc.source.loc.x, rg.to_str(arc.source.id)))
    for buh in wire.data().belsUphill:
        print("     <-| R{}C{}_{}.{}".format(buh.bel.loc.y, buh.bel.loc.x, rg.to_str(buh.bel.id), rg.to_str(buh.pin)))
    print()
