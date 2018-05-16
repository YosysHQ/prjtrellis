import diamond
import isptcl
import fuzzloops

"""
This module provides a flexible, generic interconnect fuzzer that can be adapted
to a number of different cases using filter predicates and other options.

The modus operandi is to first enumerate the nets at the location of interest
using the ispTcl API, then find arcs on those nets again with Tcl.

Then, bitstreams for each arc possibility are created and analysed using PyTrellis.
These are then compared to determine the mux enable bits for that arc.
"""


def fuzz_interconnect(config,
                      location,
                      netname_predicate=lambda x: True,
                      arc_predicate=lambda x: True,
                      netname_filter_union=False):
    """
    The fully-automatic interconnect fuzzer function. This performs the fuzzing and updates the database with the
    results. It is expected that PyTrellis has already been initialised with the database prior to this function being
    called.

    :param config: FuzzConfig instance containing target device and tile(s) of interest
    :param location: The grid location to analyse as a (row, col) tuple. This is the grid location passed to the Tcl
    API, which corresponds to the location of the site of interest, which for non-CIBs is not necessarily the same as
    the tile location but the location at which the item of interest appears in the floorplan.
    :param netname_predicate: a predicate function which should return True if a netname is of interest
    :param arc_predicate: a predicate function which should return True if an arc, as a (source, sink) tuple, is of
    interest.
    :param netname_filter_union: if True, arcs will be included if either net passes netname_predicate, if False both
    nets much pass the predicate.
    """
    nets = isptcl.get_wires_at_position(config.ncd_prf, location)
    fuzz_interconnect_with_netnames(config, nets, netname_predicate, arc_predicate, False, netname_filter_union)

def fuzz_interconnect_with_netnames(
        config,
        netnames,
        netname_predicate=lambda x: True,
        arc_predicate=lambda x: True,
        bidir=False,
        netname_filter_union=False):
    """
    Fuzz interconnect given a list of netnames to analyse. Arcs associated these netnames will be found using the Tcl
    API and bits identified as described above.

    :param config: FuzzConfig instance containing target device and tile(s) of interest
    :param netnames: A list of netnames in Lattice (un-normalised) format to analyse
    :param netname_predicate: a predicate function which should return True if a netname is of interest
    :param arc_predicate: a predicate function which should return True if an arc, as a (source, sink) tuple, is of
    interest.
    :param bidir: if True, arcs driven by as well as driving the given netnames will be considered during analysis
    :param netname_filter_union: if True, arcs will be included if either net passes netname_predicate, if False both
    nets much pass the predicate.
    """
    def per_netname(net):
        assoc_arcs = isptcl.get_arcs_on_wire(config.ncd_prf, net, not bidir)
        if netname_filter_union:
            assoc_arcs = filter(lambda x: netname_predicate(x[0]) and netname_predicate(x[1]), assoc_arcs)
        else:
            assoc_arcs = filter(lambda x: netname_predicate(x[0]) or netname_predicate(x[1]), assoc_arcs)
        fuzz_arcs = filter(arc_predicate, assoc_arcs)
        for arc in fuzz_arcs:
            # - Build a NCL with the arc
            # - Compare with base bitstream
            # - Update database as applicable
            pass
    fuzzloops.parallel_foreach(netnames, per_netname)

