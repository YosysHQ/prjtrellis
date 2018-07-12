"""
This module provides a flexible, generic interconnect fuzzer that can be adapted
to a number of different cases using filter predicates and other options.

The modus operandi is to first enumerate the nets at the location of interest
using the ispTcl API, then find arcs on those nets again with Tcl.

Then, bitstreams for each arc possibility are created and analysed using PyTrellis.
These are then compared to determine the mux enable bits for that arc.
"""
import threading
import re

import isptcl
import fuzzloops
import pytrellis
import nets
import tiles


def fuzz_interconnect(config,
                      location,
                      netname_predicate=lambda x, nets: True,
                      arc_predicate=lambda x, nets: True,
                      fc_predicate=lambda x, nets: True,
                      netname_filter_union=False,
                      enable_span1_fix=False,
                      func_cib=False,
                      fc_prefix="",
                      nonlocal_prefix=""):
    """
    The fully-automatic interconnect fuzzer function. This performs the fuzzing and updates the database with the
    results. It is expected that PyTrellis has already been initialised with the database prior to this function being
    called.

    :param config: FuzzConfig instance containing target device and tile(s) of interest
    :param location: The grid location to analyse as a (row, col) tuple. This is the grid location passed to the Tcl
    API, which corresponds to the location of the site of interest, which for non-CIBs is not necessarily the same as
    the tile location but the location at which the item of interest appears in the floorplan.
    :param netname_predicate: a predicate function which should return True if a netname is of interest, given
    the netname and the set of all nets
    :param arc_predicate: a predicate function which should return True if an arc, given the arc as a (source, sink)
    tuple and the set of all netnames, is of interest
    :param fc_predicate: a predicate function which should return True if a fixed connection should be included
    :param netname_filter_union: if True, arcs will be included if either net passes netname_predicate, if False both
    nets much pass the predicate.
    :param enable_span1_fix: if True, include span1 wires that are excluded due to a Tcl API bug
    :param func_cib: if True, we are fuzzing a special function to CIB interconnect, enable optimisations for this
    :param fc_prefix: add a prefix to non-global fixed connections for device-specific fuzzers
    :param nonlocal_prefix: add a prefix to non-global and non-neighbour wires for device-specific fuzzers
    """
    netdata = isptcl.get_wires_at_position(config.ncd_prf, location)
    netnames = [x[0] for x in netdata]
    if enable_span1_fix:
        extra_netnames = []
        for net in netnames:
            m = re.match("R(\d+)C(\d+)_V01N(\d{4})", net)
            if m:
                row = int(m.group(1))
                col = int(m.group(2))
                idn = m.group(3)
                if row == location[0] + 1 and col == location[1]:
                    fixednet = "R{}C{}_V01N{}".format(location[0] - 1, col, idn)
                    print("added {}".format(fixednet))
                    extra_netnames.append(fixednet)
        netnames = extra_netnames + netnames
    if func_cib and not netname_filter_union:
        netnames = list(filter(lambda x: netname_predicate(x, netnames), netnames))
    fuzz_interconnect_with_netnames(config, netnames, netname_predicate, arc_predicate, fc_predicate, func_cib,
                                    netname_filter_union, False, fc_prefix, nonlocal_prefix)


def fuzz_interconnect_with_netnames(
        config,
        netnames,
        netname_predicate=lambda x, nets: True,
        arc_predicate=lambda x, nets: True,
        fc_predicate=lambda x, nets: True,
        bidir=False,
        netname_filter_union=False,
        full_mux_style=False,
        fc_prefix="",
        nonlocal_prefix=""):
    """
    Fuzz interconnect given a list of netnames to analyse. Arcs associated these netnames will be found using the Tcl
    API and bits identified as described above.

    :param config: FuzzConfig instance containing target device and tile(s) of interest
    :param netnames: A list of netnames in Lattice (un-normalised) format to analyse
    :param netname_predicate: a predicate function which should return True if a netname is of interest, given
    the netname and the set of all nets
    :param arc_predicate: a predicate function which should return True if an arc, given the arc as a (source, sink)
    tuple and the set of all netnames, is of interest
    :param bidir: if True, arcs driven by as well as driving the given netnames will be considered during analysis
    :param netname_filter_union: if True, arcs will be included if either net passes netname_predicate, if False both
    nets much pass the predicate.
    :param full_mux_style: if True, is a full mux, and all 0s is considered a valid config bit possibility
    :param fc_prefix: add a prefix to non-global fixed connections for device-specific fuzzers
    """
    net_arcs = isptcl.get_arcs_on_wires(config.ncd_prf, netnames, not bidir)
    baseline_bitf = config.build_design(config.ncl, {}, "base_")
    baseline_chip = pytrellis.Bitstream.read_bit(baseline_bitf).deserialise_chip()

    max_row = baseline_chip.get_max_row()
    max_col = baseline_chip.get_max_col()

    def normalise_arc_in_tile(tile, arc):
        return tuple(nets.normalise_name((max_row, max_col), tile, x) for x in arc)

    def add_nonlocal_prefix(wire):
        if wire.startswith("G_"):
            return wire
        m = re.match(r'([NS]\d+)?([EW]\d+)?_.*', wire)
        if m:
            for g in m.groups():
                if g is not None and int(g[1:]) >= 3:
                    return nonlocal_prefix + wire
        return wire

    def per_netname(net):
        # Get a unique prefix from the thread ID
        prefix = "thread{}_".format(threading.get_ident())
        assoc_arcs = net_arcs[net]
        # Obtain the set of databases
        tile_dbs = {tile: pytrellis.get_tile_bitdata(
            pytrellis.TileLocator(config.family, config.device, tiles.type_from_fullname(tile))) for tile in
            config.tiles}
        # First filter using netname predicate
        if netname_filter_union:
            assoc_arcs = filter(lambda x: netname_predicate(x[0], netnames) and netname_predicate(x[1], netnames),
                                assoc_arcs)
        else:
            assoc_arcs = filter(lambda x: netname_predicate(x[0], netnames) or netname_predicate(x[1], netnames),
                                assoc_arcs)
        # Then filter using the arc predicate
        fuzz_arcs = list(filter(lambda x: arc_predicate(x, netnames), assoc_arcs))

        # Ful fullmux mode only
        changed_bits = set()
        arc_tiles = {}
        tiles_changed = set()

        for arc in fuzz_arcs:
            # Route statement containing arc for NCL file
            arc_route = "route\n\t\t\t" + arc[0] + "." + arc[1] + ";"
            # Build a bitstream and load it using libtrellis
            arc_bitf = config.build_design(config.ncl, {"route": arc_route}, prefix)
            arc_chip = pytrellis.Bitstream.read_bit(arc_bitf).deserialise_chip()
            # Compare the bitstream with the arc to the baseline bitstream
            diff = arc_chip - baseline_chip
            if (not full_mux_style) or len(fuzz_arcs) == 1:
                if len(diff) == 0:
                    # No difference means fixed interconnect
                    # We consider this to be in the first tile if multiple tiles are being analysed
                    if fc_predicate(arc, netnames):
                        norm_arc = normalise_arc_in_tile(config.tiles[0], arc)
                        fc = pytrellis.FixedConnection()
                        norm_arc = [fc_prefix + _ if not _.startswith("G_") else _ for _ in norm_arc]
                        norm_arc = [add_nonlocal_prefix(_) for _ in norm_arc]
                        fc.source, fc.sink = norm_arc
                        tile_dbs[config.tiles[0]].add_fixed_conn(fc)
                else:
                    for tile in config.tiles:
                        if tile in diff:
                            # Configurable interconnect in <tile>
                            norm_arc = normalise_arc_in_tile(tile, arc)
                            norm_arc = [add_nonlocal_prefix(_) for _ in norm_arc]
                            ad = pytrellis.ArcData()
                            ad.source, ad.sink = norm_arc
                            ad.bits = pytrellis.BitGroup(diff[tile])
                            tile_dbs[tile].add_mux_arc(ad)
            else:
                arc_tiles[arc] = {}
                for tile in config.tiles:
                    if tile in diff:
                        tiles_changed.add(tile)
                        for bit in diff[tile]:
                            changed_bits.add((tile, bit.frame, bit.bit))
                    arc_tiles[arc][tile] = arc_chip.tiles[tile]

        if full_mux_style and len(fuzz_arcs) > 1:
            for tile in tiles_changed:
                for arc in arc_tiles:
                    bg = pytrellis.BitGroup()
                    for (btile, bframe, bbit) in changed_bits:
                        if btile == tile:
                            state = arc_tiles[arc][tile].cram.bit(bframe, bbit)
                            cb = pytrellis.ConfigBit()
                            cb.frame = bframe
                            cb.bit = bbit
                            cb.inv = (state == 0)
                            bg.bits.add(cb)
                    ad = pytrellis.ArcData()
                    ad.source, ad.sink = normalise_arc_in_tile(tile, arc)
                    ad.bits = bg
                    tile_dbs[tile].add_mux_arc(ad)
        # Flush database to disk
        for tile, db in tile_dbs.items():
            db.save()

    fuzzloops.parallel_foreach(netnames, per_netname)
