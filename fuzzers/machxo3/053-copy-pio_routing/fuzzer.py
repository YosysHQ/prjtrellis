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
pio_tiles_l0 = {
    "PIC_L0_VREF3" : (lambda a: True, lambda c: True),
    "PIC_L0_DUMMY" : (exclude_abcd_conns, exclude_abcd_conns),
}

pio_tiles_l0_9400 = {
    "PIC_L0_VREF4" : (lambda a: True, lambda c: True),
    "PIC_L0_VREF5" : (lambda a: True, lambda c: True),
}

pio_tiles_l1 = {
    "PIC_L1_VREF4" : (lambda a: True, lambda c: True),
    "PIC_L1_VREF5" : (lambda a: True, lambda c: True),
    "PIC_L1_DUMMY" : (exclude_abcd_conns, exclude_abcd_conns),
}

pio_tiles_l2 = {
    "PIC_L2_VREF4" : (lambda a: True, lambda c: True),
    "PIC_L2_VREF5" : (lambda a: True, lambda c: True),
    "PIC_L2_DUMMY" : (exclude_abcd_conns, exclude_abcd_conns),
}

pio_tiles_l3 = {
    "PIC_L3_VREF4" : (lambda a: True, lambda c: True),
    "PIC_L3_VREF5" : (lambda a: True, lambda c: True),
}

pio_tiles_r0 = {
    "PIC_R0_DUMMY" : (exclude_abcd_conns, exclude_abcd_conns),
}

pio_tiles_r1 = {
    "PIC_R1_DUMMY" : (exclude_abcd_conns, exclude_abcd_conns),
}

pio_tiles_cib = {
    "URC0" : (exclude_globals, exclude_globals),
    "URC1" : (exclude_globals, exclude_globals)
}

def main():
    pytrellis.load_database("../../../database")

    for dest, pred in pio_tiles_l0.items():
        dbcopy.copy_muxes_with_predicate("MachXO3", "LCMXO3LF-1300E", "PIC_L0", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3", "LCMXO3LF-1300E", "PIC_L0", dest, pred[1])

    for dest, pred in pio_tiles_l0_9400.items():
        dbcopy.copy_muxes_with_predicate("MachXO3", "LCMXO3LF-9400C", "PIC_L0", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3", "LCMXO3LF-9400C", "PIC_L0", dest, pred[1])

    for dest, pred in pio_tiles_l1.items():
        dbcopy.copy_muxes_with_predicate("MachXO3", "LCMXO3LF-4300C", "PIC_L1", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3", "LCMXO3LF-4300C", "PIC_L1", dest, pred[1])

    for dest, pred in pio_tiles_l2.items():
        dbcopy.copy_muxes_with_predicate("MachXO3", "LCMXO3LF-6900C", "PIC_L2", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3", "LCMXO3LF-6900C", "PIC_L2", dest, pred[1])

    for dest, pred in pio_tiles_l3.items():
        dbcopy.copy_muxes_with_predicate("MachXO3", "LCMXO3LF-2100C", "PIC_L3", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3", "LCMXO3LF-2100C", "PIC_L3", dest, pred[1])


    for dest, pred in pio_tiles_r0.items():
        dbcopy.copy_muxes_with_predicate("MachXO3", "LCMXO3LF-1300C", "PIC_R0", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3", "LCMXO3LF-1300C", "PIC_R0", dest, pred[1])

    for dest, pred in pio_tiles_r1.items():
        dbcopy.copy_muxes_with_predicate("MachXO3", "LCMXO3LF-6900C", "PIC_R1", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3", "LCMXO3LF-6900C", "PIC_R1", dest, pred[1])

    for dest, pred in pio_tiles_cib.items():
        dbcopy.copy_muxes_with_predicate("MachXO3", "LCMXO3LF-1300E", "CIB_PIC_T0", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3", "LCMXO3LF-1300E", "CIB_PIC_T0", dest, pred[1])


if __name__ == "__main__":
    main()
