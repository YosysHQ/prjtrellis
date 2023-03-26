import dbfixup
import pytrellis

def main():
    pytrellis.load_database("../../../database")
    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-1300E", "PIC_L0", (29, 11))
    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-1300E", "PIC_L0_VREF3", (29, 11))
    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-1300E", "PIC_L0_VREF4", (29, 11))
    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-1300E", "PIC_L0_VREF5", (29, 11))

    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-4300C", "PIC_L1", (29, 11))
    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-4300C", "PIC_L1_VREF4", (29, 11))
    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-4300C", "PIC_L1_VREF5", (29, 11))

    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-6900C", "PIC_L2", (29, 11))
    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-6900C", "PIC_L2_VREF4", (29, 11))
    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-6900C", "PIC_L2_VREF5", (29, 11))

    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-2100C", "PIC_L3", (29, 11))
    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-2100C", "PIC_L3_VREF4", (29, 11))
    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-2100C", "PIC_L3_VREF5", (29, 11))
    
    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-1300E", "PIC_R0", (29, 59), (0, 48))

    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-6900C", "PIC_R1", (29, 59), (0, 48))

    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-1300E", "PIC_LS0", (29, 11))
    
    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-1300E", "PIC_RS0", (29, 59), (0, 48))

if __name__ == "__main__":
    main()
