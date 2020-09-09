import dbfixup
import pytrellis

def main():
    pytrellis.load_database("../../../database")
    dbfixup.remove_enum_bits("MachXO2", "LCMXO2-1200HC", "PIC_L0", (29, 11))
    dbfixup.remove_enum_bits("MachXO2", "LCMXO2-1200HC", "PIC_R0", (29, 59), (0, 48))

if __name__ == "__main__":
    main()
