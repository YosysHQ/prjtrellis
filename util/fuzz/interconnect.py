"""
This module provides a flexible, generic interconnect fuzzer that can be adapted
to a number of different cases using filter predicates and other options.

The modus operandi is to first enumerate the nets at the location of interest
using the ispTcl API, then find arcs on those nets again with Tcl.

Then, bitstreams for each arc possibility are created and analysed using PyTrellis.
These are then compared to determine the mux enable bits for that arc.
"""
import threading

import isptcl
import fuzzloops
import pytrellis
import nets
import tiles


def fuzz_interconnect(config,
                      location,
                      netname_predicate=lambda x, nets: True,
                      arc_predicate=lambda x, nets: True,
                      netname_filter_union=False):
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
    :param netname_filter_union: if True, arcs will be included if either net passes netname_predicate, if False both
    nets much pass the predicate.
    """
    nets = isptcl.get_wires_at_position(config.ncd_prf, location)
    fuzz_interconnect_with_netnames(config, nets, netname_predicate, arc_predicate, False, netname_filter_union)


def fuzz_interconnect_with_netnames(
        config,
        netnames,
        netname_predicate=lambda x, nets: True,
        arc_predicate=lambda x, nets: True,
        bidir=False,
        netname_filter_union=False):
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
    """
    net_arcs = isptcl.get_arcs_on_wires(config.ncd_prf, netnames, not bidir)
    baseline_bitf = config.build_design(config.ncl, {}, "base_")
    baseline_chip = pytrellis.Bitstream.read_bit(baseline_bitf).deserialise_chip()

    max_row = baseline_chip.get_max_row()
    max_col = baseline_chip.get_max_col()

    def normalise_arc_in_tile(tile, arc):
        return tuple(nets.normalise_name((max_row, max_col), tile, x) for x in arc)

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
        fuzz_arcs = filter(lambda x: arc_predicate(x, netnames), assoc_arcs)
        for arc in fuzz_arcs:
            # Route statement containing arc for NCL file
            arc_route = "route\n\t\t\t" + arc[0] + "." + arc[1] + ";"
            # Build a bitstream and load it using libtrellis
            arc_bitf = config.build_design(config.ncl, {"route": arc_route}, prefix)
            arc_chip = pytrellis.Bitstream.read_bit(arc_bitf).deserialise_chip()
            # Compare the bitstream with the arc to the baseline bitstream
            diff = arc_chip - baseline_chip
            if len(diff) == 0:
                # No difference means fixed interconnect
                # We consider this to be in the first tile if multiple tiles are being analysed
                norm_arc = normalise_arc_in_tile(config.tiles[0], arc)
                fc = pytrellis.FixedConnection()
                fc.source, fc.sink = norm_arc
                tile_dbs[config.tiles[0]].add_fixed_conn(fc)
            else:
                for tile in config.tiles:
                    if tile in diff:
                        # Configurable interconnect in <tile>
                        norm_arc = normalise_arc_in_tile(tile, arc)
                        ad = pytrellis.ArcData()
                        ad.source, ad.sink = norm_arc
                        ad.bits = pytrellis.BitGroup(diff[tile])
                        tile_dbs[tile].add_mux_arc(ad)
        # Flush database to disk
        for tile, db in tile_dbs.items():
            db.save()

    fuzzloops.parallel_foreach(netnames, per_netname)
