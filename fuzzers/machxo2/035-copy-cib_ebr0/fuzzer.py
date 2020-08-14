import dbcopy
import pytrellis
import nets

# Based on prior fuzzing conjecture that CIB_EBR
# 0,1,2, and DUMMY, and CIB_PIC_B0 and CIB_PIC_B_DUMMY have the same layout.

# Pending dbcopy and prjtrellis changes (TODO), CIB_PIC_B0 and CIB_PIC_B_DUMMY
# need to be manually tweaked to convert U_/D_ prefixes to G_ prefixes. There's
# too much shared routing to justify rerunning the fuzzers.

shared_tiles = ["CIB_EBR1", "CIB_EBR2", "CIB_EBR_DUMMY"]
shared_tiles_no_lrudconns = ["CIB_PIC_B0", "CIB_PIC_B_DUMMY"]

# Only globals are the BRANCH connections which are fed by U_/D_ conns with
# G_ prefixes (muxed).
def exclude_lrud_conns(conn):
    src = conn.source
    sink = conn.sink

    return not (src.startswith("G_CLKO") or sink.startswith("G_CLKI"))

def main():
    pytrellis.load_database("../../../database")

    for dest in shared_tiles:
        dbcopy.dbcopy("MachXO2", "LCMXO2-1200HC", "CIB_EBR0", dest)

    for dest in shared_tiles_no_lrudconns:
        dbcopy.dbcopy("MachXO2", "LCMXO2-1200HC", "CIB_EBR0", dest, copy_conns=False)
        dbcopy.copy_conns_with_predicate("MachXO2", "LCMXO2-1200HC", "CIB_EBR0", dest, exclude_lrud_conns)

if __name__ == "__main__":
    main()
