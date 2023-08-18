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
    "PIC_L0_I3C" : (lambda a: True, lambda c: True, include_abcd_enum),
    "LLC0PIC_I3C_VREF3" : (lambda a: False, lambda c: False, include_abcd_enum),
    "PIC_L1" : (lambda a: False, lambda c: False, include_abcd_enum),
    "PIC_L0_VREF4" : (lambda a: True, lambda c: True, include_abcd_enum),
    "PIC_L0_VREF5" : (lambda a: True, lambda c: True, include_abcd_enum),
}

pio_tiles_l1 = {
    "PIC_L1_I3C" : (lambda a: True, lambda c: True, include_abcd_enum),
    "PIC_L1_VREF4" : (lambda a: True, lambda c: True, include_abcd_enum),
    "PIC_L1_VREF5" : (lambda a: True, lambda c: True, include_abcd_enum),
}

pio_tiles_r1 = {
    "LRC1PIC2" : (lambda a: False, lambda c: False, include_abcd_enum),
}

def main():
    pytrellis.load_database("../../../database")

    for dest, pred in pio_tiles_l0.items():
        dbcopy.copy_muxes_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_L0", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_L0", dest, pred[1])
        dbcopy.copy_enums_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_L0", dest, pred[2], True)

    for dest, pred in pio_tiles_l1.items():
        dbcopy.copy_muxes_with_predicate("MachXO3D", "LCMXO3D-4300C", "PIC_L1", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3D", "LCMXO3D-4300C", "PIC_L1", dest, pred[1])
        dbcopy.copy_enums_with_predicate("MachXO3D", "LCMXO3D-4300C", "PIC_L1", dest, pred[2])

    for dest, pred in pio_tiles_r1.items():
        dbcopy.copy_muxes_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_R1", dest, pred[0])
        dbcopy.copy_conns_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_R1", dest, pred[1])
        dbcopy.copy_enums_with_predicate("MachXO3D", "LCMXO3D-9400HC", "PIC_R1", dest, pred[2])


if __name__ == "__main__":
    main()
