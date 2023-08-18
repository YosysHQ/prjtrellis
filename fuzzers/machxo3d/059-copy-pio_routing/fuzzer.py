import dbcopy
import pytrellis

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

def include_abcd_enum(conn):
    if isinstance(conn, pytrellis.EnumSettingBits):
        name = conn.name
    else:
        name = ""
    if (name.startswith("PIOA.") or name.startswith("PIOB.")
        or name.startswith("PIOC.") or name.startswith("PIOD.")):
        return True
    return False

def include_ab_enum(conn):
    if isinstance(conn, pytrellis.EnumSettingBits):
        name = conn.name
    else:
        name = ""
    if (name.startswith("PIOA.") or name.startswith("PIOB.")):
        return True
    return False


# Key: (Mux Predicate, Conn Predicate, Enum Predicate)
pio_tiles_l0 = {
    "PIC_L0_VREF4" : (lambda a: True, lambda c: True, lambda e: True),
    "PIC_L0_VREF5" : (lambda a: True, lambda c: True, lambda e: True),
    "PIC_L0_I3C" : (lambda a: True, lambda c: True, lambda e: False),
    "PIC_L0_DUMMY" : (exclude_abcd_conns, exclude_abcd_conns, lambda e: False),
    "PIC_L1" : (lambda a: False, lambda c: False, include_abcd_enum),
}

pio_tiles_l1 = {
    "PIC_L1_I3C" : (lambda a: True, lambda c: True, lambda e: False),
    "PIC_L1_VREF4" : (lambda a: True, lambda c: True, lambda e: True),
    "PIC_L1_VREF5" : (lambda a: True, lambda c: True, lambda e: True),
    "PIC_L1_DUMMY" : (exclude_abcd_conns, exclude_abcd_conns, lambda e: False),
}

pio_tiles_l0_i3c = {
    "LLC0PIC_I3C_VREF3" : (lambda a: False, lambda c: False, include_abcd_enum),
    "PIC_L1_I3C" : (lambda a: False, lambda c: False, include_abcd_enum),
}

pio_tiles_r1 = {
    "PIC_R1_DUMMY" : (exclude_abcd_conns, exclude_abcd_conns, lambda e: False),
    "LRC1PIC2" : (lambda a: False, lambda c: False, include_abcd_enum),
}

pio_tiles_t_cib = {
    "CIB_PIC_T_DUMMY" : (lambda a: True, lambda c: True, lambda e: False),
    "CIB_CFG0" : (lambda a: True, lambda c: True, lambda e: False),
    "CIB_CFG1" : (lambda a: True, lambda c: True, lambda e: False),
    "CIB_CFG2" : (lambda a: True, lambda c: True, lambda e: False),
    "CIB_CFG3" : (lambda a: True, lambda c: True, lambda e: False),
}

pio_tiles_b_cib = {
    "CIB_PIC_B_DUMMY" : (lambda a: True, lambda c: True, lambda e: False),
}

def main():
    pytrellis.load_database("../../../database")

    for dest, pred in pio_tiles_l0.items():
        dbcopy.copy_muxes_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_L0", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_L0", dest, pred[1])
        dbcopy.copy_enums_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_L0", dest, pred[2], True)

    for dest, pred in pio_tiles_l1.items():
        dbcopy.copy_muxes_with_predicate("MachXO3D", "LCMXO3D-4300HC", "PIC_L1", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3D", "LCMXO3D-4300HC", "PIC_L1", dest, pred[1])
        dbcopy.copy_enums_with_predicate("MachXO3D", "LCMXO3D-4300HC", "PIC_L1", dest, pred[2], True)

    for dest, pred in pio_tiles_l0_i3c.items():
        dbcopy.copy_muxes_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_L0_I3C", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_L0_I3C", dest, pred[1])
        dbcopy.copy_enums_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_L0_I3C", dest, pred[2])

    for dest, pred in pio_tiles_r1.items():
        dbcopy.copy_muxes_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_R1", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_R1", dest, pred[1])
        dbcopy.copy_enums_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_R1", dest, pred[2])

    for dest, pred in pio_tiles_t_cib.items():
        dbcopy.copy_muxes_with_predicate("MachXO3D", "LCMXO3D-9400HC", "CIB_PIC_T0", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3D", "LCMXO3D-9400HC", "CIB_PIC_T0", dest, pred[1])
        dbcopy.copy_enums_with_predicate("MachXO3D", "LCMXO3D-9400HC", "CIB_PIC_T0", dest, pred[2])

    for dest, pred in pio_tiles_b_cib.items():
        dbcopy.copy_muxes_with_predicate("MachXO3D", "LCMXO3D-9400HC", "CIB_PIC_B0", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3D", "LCMXO3D-9400HC", "CIB_PIC_B0", dest, pred[1])
        dbcopy.copy_enums_with_predicate("MachXO3D", "LCMXO3D-9400HC", "CIB_PIC_B0", dest, pred[2])

if __name__ == "__main__":
    main()
