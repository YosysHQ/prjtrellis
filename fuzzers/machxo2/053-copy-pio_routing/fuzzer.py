import dbcopy
import pytrellis
import nets

# In the below filters: accept HF/HL/and HBSX fixed connections to be copied
# for now.
def exclude_abcd_conns(conn):
    if isinstance(conn, pytrellis.FixedConnection):
        src = conn.source
        sink = conn.sink
    else:
        (src, sink) = conn
    if (src.endswith("A") or "A_" in src
        or src.endswith("B") or "B_" in src
        or src.endswith("C") or "C_" in src
        or src.endswith("D") or "D_" in src):
        return False
    elif (sink.endswith("A") or "A_" in sink
          or sink.endswith("B") or "B_" in sink
          or sink.endswith("C") or "C_" in sink
          or sink.endswith("D") or "D_" in sink):
        return False
    else:
        return True

def exclude_cd_conns(conn):
    if isinstance(conn, pytrellis.FixedConnection):
        src = conn.source
        sink = conn.sink
    else:
        (src, sink) = conn
    if src.endswith("C") or "C_" in src or src.endswith("D") or "D_" in src:
        return False
    elif sink.endswith("C") or "C_" in sink or sink.endswith("D") or "D_" in sink:
        return False
    else:
        return True

# URC0 has same routing as `CIB_PIC_T`, but the globals are unique.
def exclude_globals(conn):
    if isinstance(conn, pytrellis.FixedConnection):
        src = conn.source
        sink = conn.sink
    else:
        (src, sink) = conn
    return not (src.startswith("G_") and (sink.startswith("BRANCH_") or sink.startswith("G_")))

def include_globals_only(conn):
    return not exclude_globals(conn)

# Key: (Mux Predicate, Conn Predicate)
pio_tiles_l = {
    "PIC_LS0" : (exclude_cd_conns, exclude_cd_conns),
    "PIC_L0_VREF3" : (lambda a: True, lambda c: True),
    "PIC_L0_DUMMY" : (exclude_abcd_conns, exclude_abcd_conns),
    "LLC0" : (exclude_abcd_conns, exclude_abcd_conns),
}

pio_tiles_r = {
    "PIC_RS0" : (exclude_cd_conns, exclude_cd_conns),
    "PIC_R0_DUMMY" : (exclude_abcd_conns, exclude_abcd_conns),
    "LRC0" : (exclude_abcd_conns, exclude_abcd_conns),
}

pio_tiles_cib = {
    "URC0" : (exclude_globals, exclude_globals)
}

def main():
    pytrellis.load_database("../../../database")

    for dest, pred in pio_tiles_l.items():
        dbcopy.copy_muxes_with_predicate("MachXO2", "LCMXO2-1200HC", "PIC_L0", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO2", "LCMXO2-1200HC", "PIC_L0", dest, pred[1])

    for dest, pred in pio_tiles_r.items():
        dbcopy.copy_muxes_with_predicate("MachXO2", "LCMXO2-1200HC", "PIC_R0", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO2", "LCMXO2-1200HC", "PIC_R0", dest, pred[1])

    for dest, pred in pio_tiles_cib.items():
        dbcopy.copy_muxes_with_predicate("MachXO2", "LCMXO2-1200HC", "CIB_PIC_T0", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO2", "LCMXO2-1200HC", "CIB_PIC_T0", dest, pred[1])


if __name__ == "__main__":
    main()
