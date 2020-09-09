import pytrellis

# Taken from ECP5. Using R5C10 as an example, R5C11_HFIE0000, or "E1_HFIE0000"
# will not be considered part of the current tile by isptcl.get_wires_at_position
# when invoked via fuzz_interconnect (unless possibly func_cib=True- untested).
#
# However, R5C10_HFIE0000, or "HFIE0000" is considered part of the current tile.
# When netname_filter_union=True*, as is the default of fuzz_interconnect,
# the arc R5C9_FCO --> R5C10_HFIE0000 gets filtered out by netname_predicate
# because "R5C9_FCO" is not part of the current tile.
#
# We can special-case "R5C9_FCO" in the netname_predicate, but it feels more
# natural to have carry out (FCO) be the _source_ connection to the next tile,
# rather than the sink connection from the previous tile
# (e.g. R5C10_FCO --> R5C11_HFIE0000 is preferable to
# R5C9_FCO --> R5C10_HFIE0000 --> R5C10_FCI).
#
# * Which should really be named netname_filter_intersect.

def main():
    pytrellis.load_database("../../../database")
    db = pytrellis.get_tile_bitdata(pytrellis.TileLocator("MachXO2", "LCMXO2-1200HC", "PLC"))
    fc = pytrellis.FixedConnection()
    fc.source = "FCO"
    fc.sink = "E1_HFIE0000"
    db.add_fixed_conn(fc)
    db.save()

if __name__ == "__main__":
    main()
