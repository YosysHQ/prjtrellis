import dbcopy
import pytrellis
import nets

# Based on prior fuzzing conjecture that CIB_EBR
# 0,1,2, and DUMMY have the same layout.

shared_tiles = ["CIB_EBR1", "CIB_EBR2", "CIB_EBR_DUMMY"]

def main():
    pytrellis.load_database("../../../database")

    for dest in shared_tiles:
        dbcopy.dbcopy("MachXO2", "LCMXO2-1200HC", "CIB_EBR0", dest)


if __name__ == "__main__":
    main()
