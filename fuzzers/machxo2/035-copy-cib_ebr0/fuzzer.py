import dbcopy
import pytrellis

# Based on prior fuzzing that wasn't committed, conjecture that CIB_EBR
# 0,1,2, and DUMMY have the same layout.

def main():
    pytrellis.load_database("../../../database")
    dbcopy.dbcopy("MachXO2", "LCMXO2-1200HC", "CIB_EBR0", "CIB_EBR1")
    dbcopy.dbcopy("MachXO2", "LCMXO2-1200HC", "CIB_EBR0", "CIB_EBR2")
    dbcopy.dbcopy("MachXO2", "LCMXO2-1200HC", "CIB_EBR0", "CIB_EBR_DUMMY")


if __name__ == "__main__":
    main()
