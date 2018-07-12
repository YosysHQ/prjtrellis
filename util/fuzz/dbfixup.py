import pytrellis

"""
Database fix utility

Run at the end of fuzzing to "finalise" the database and remove problems that may occur during fuzzing
"""


def dbfixup(family, device, tiletype):
    db = pytrellis.get_tile_bitdata(
        pytrellis.TileLocator(family, device, tiletype))

    fc = db.get_fixed_conns()
    # Where a wire is driven by both a mux and fixed connections, replace those fixed connections
    # with a mux arc with no config bits
    for mux in db.get_sinks():
        deleteFc = False
        for conn in fc:
            if conn.sink == mux:
                ad = pytrellis.ArcData()
                ad.source = conn.source
                ad.sink = conn.sink
                db.add_mux_arc(ad)
                deleteFc = True
        if deleteFc:
            db.remove_fixed_sink(mux)
    db.save()
