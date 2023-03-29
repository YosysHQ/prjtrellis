import dbfixup
import pytrellis

def main():
    pytrellis.load_database("../../../database")
    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-1300E", "PIC_L0", (29, 11))
  
    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-1300E", "PIC_R0", (29, 59), (0, 48))

    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-2100C", "ULC3PIC", (29, 11))

    dbfixup.remove_enum_bits("MachXO3", "LCMXO3LF-2100C", "URC1PIC", (29, 59), (0, 48))
if __name__ == "__main__":
    main()
