import dbcopy
import pytrellis


def include_abcd_enum(conn):
    if isinstance(conn, pytrellis.EnumSettingBits):
        name = conn.name
    else:
        name = ""
    if (name.startswith("PIOA.") or name.startswith("PIOB.")
        or name.startswith("PIOC.") or name.startswith("PIOD.")
        or name.startswith("IOLOGICA.") or name.startswith("IOLOGICB.")
        or name.startswith("IOLOGICC.") or name.startswith("IOLOGICD.")):
        return True
    return False

def include_ab_enum(conn):
    if isinstance(conn, pytrellis.EnumSettingBits):
        name = conn.name
    else:
        name = ""
    if (name.startswith("PIOA.") or name.startswith("PIOB.")
        or name.startswith("IOLOGICA.") or name.startswith("IOLOGICB.")):
        return True
    return False


# Key: (Mux Predicate, Conn Predicate, Enum Predicate)
pio_tiles_l0 = {
    "PIC_L0_VREF3" : (lambda a: True, lambda c: True, include_abcd_enum),
    "LLC3PIC_VREF3" : (lambda a: False, lambda c: False, include_abcd_enum),
    "PIC_LS0" : (lambda a: False, lambda c: False, include_ab_enum),
    "PIC_L1" : (lambda a: False, lambda c: False, include_abcd_enum),
    "PIC_L2" : (lambda a: False, lambda c: False, include_abcd_enum),
    "PIC_L3" : (lambda a: False, lambda c: False, include_abcd_enum),
}

pio_tiles_l1 = {
    "PIC_L1_VREF4" : (lambda a: True, lambda c: True, include_abcd_enum),
    "PIC_L1_VREF5" : (lambda a: True, lambda c: True, include_abcd_enum),
}

pio_tiles_l2 = {
    "PIC_L2_VREF4" : (lambda a: True, lambda c: True, include_abcd_enum),
    "PIC_L2_VREF5" : (lambda a: True, lambda c: True, include_abcd_enum),
}

pio_tiles_l3 = {
    "PIC_L3_VREF4" : (lambda a: True, lambda c: True, include_abcd_enum),
    "PIC_L3_VREF5" : (lambda a: True, lambda c: True, include_abcd_enum),
}

pio_tiles_r0 = {
    "PIC_R1" : (lambda a: False, lambda c: False, include_abcd_enum),
    "PIC_RS0" : (lambda a: False, lambda c: False, include_ab_enum),
}

pio_tiles_r1 = {
    "LRC1PIC2" : (lambda a: False, lambda c: False, include_abcd_enum),
}

def main():
    pytrellis.load_database("../../../database")

    for dest, pred in pio_tiles_l0.items():
        dbcopy.copy_muxes_with_predicate("MachXO2", "LCMXO2-1200HC", "PIC_L0", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO2", "LCMXO2-1200HC", "PIC_L0", dest, pred[1])
        dbcopy.copy_enums_with_predicate("MachXO2", "LCMXO2-1200HC", "PIC_L0", dest, pred[2], True)

    for dest, pred in pio_tiles_l1.items():
        dbcopy.copy_muxes_with_predicate("MachXO2", "LCMXO2-4000HC", "PIC_L1", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO2", "LCMXO2-4000HC", "PIC_L1", dest, pred[1])
        dbcopy.copy_enums_with_predicate("MachXO2", "LCMXO2-4000HC", "PIC_L1", dest, pred[2])

    for dest, pred in pio_tiles_l2.items():
        dbcopy.copy_muxes_with_predicate("MachXO2", "LCMXO2-7000HC", "PIC_L2", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO2", "LCMXO2-7000HC", "PIC_L2", dest, pred[1])
        dbcopy.copy_enums_with_predicate("MachXO2", "LCMXO2-7000HC", "PIC_L2", dest, pred[2])

    for dest, pred in pio_tiles_l3.items():
        dbcopy.copy_muxes_with_predicate("MachXO2", "LCMXO2-2000HC", "PIC_L3", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO2", "LCMXO2-2000HC", "PIC_L3", dest, pred[1])
        dbcopy.copy_enums_with_predicate("MachXO2", "LCMXO2-2000HC", "PIC_L3", dest, pred[2])

    for dest, pred in pio_tiles_r0.items():
        dbcopy.copy_muxes_with_predicate("MachXO2", "LCMXO2-1200HC", "PIC_R0", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO2", "LCMXO2-1200HC", "PIC_R0", dest, pred[1])
        dbcopy.copy_enums_with_predicate("MachXO2", "LCMXO2-1200HC", "PIC_R0", dest, pred[2])

    for dest, pred in pio_tiles_r1.items():
        dbcopy.copy_muxes_with_predicate("MachXO2", "LCMXO2-7000HC", "PIC_R1", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO2", "LCMXO2-7000HC", "PIC_R1", dest, pred[1])
        dbcopy.copy_enums_with_predicate("MachXO2", "LCMXO2-7000HC", "PIC_R1", dest, pred[2])


if __name__ == "__main__":
    main()
