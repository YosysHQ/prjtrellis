import dbcopy
import pytrellis

# Based on prior fuzzing conjecture that CIB_EBR
# 0,1,2, and DUMMY, and CIB_PIC_B0 and CIB_PIC_B_DUMMY have the same layout.

shared_tiles = ["CIB_EBR1", "CIB_EBR2", "CIB_EBR_DUMMY", "CIB_PIC_B0", "CIB_PIC_B_DUMMY"]

def main():
    pytrellis.load_database("../../../database")

    for dest in shared_tiles:
        dbcopy.dbcopy("MachXO2", "LCMXO2-1200HC", "CIB_EBR0", dest)

if __name__ == "__main__":
    main()
