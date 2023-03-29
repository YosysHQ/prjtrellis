import dbcopy
import pytrellis
import nets

# Based on prior fuzzing conjecture that CIB_EBR
# 0,1,2, and DUMMY have the same layout.

shared_tiles = ["CIB_EBR1", "CIB_EBR2", "CIB_EBR_DUMMY"]
shared_tiles_10k = ["CIB_EBR1_10K", "CIB_EBR2_10K", "CIB_EBR_DUMMY_10K"]

def main():
    pytrellis.load_database("../../../database")

    for dest in shared_tiles:
        dbcopy.dbcopy("MachXO3", "LCMXO3-1300E", "CIB_EBR0", dest)

    for dest in shared_tiles_10k:
        dbcopy.dbcopy("MachXO3", "LCMXO3-9400C", "CIB_EBR0_10K", dest)

if __name__ == "__main__":
    main()
