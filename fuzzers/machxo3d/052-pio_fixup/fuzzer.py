import dbfixup
import pytrellis

def main():
    pytrellis.load_database("../../../database")
    dbfixup.remove_enum_bits("MachXO3D", "LCMXO3D-9400HC", "PIC_L0", (29, 11))
    dbfixup.remove_enum_bits("MachXO3D", "LCMXO3D-9400HC", "PIC_L0_I3C", (29, 11))
  
    dbfixup.remove_enum_bits("MachXO3D", "LCMXO3D-9400HC", "PIC_R1", (29, 59), (0, 48))

if __name__ == "__main__":
    main()
