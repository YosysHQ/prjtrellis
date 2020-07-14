import dbcopy
import pytrellis

# Then copy the BRANCH info from CIB_PIC_T0 back to the other tiles.
shared_tiles = ["CIB_PIC_T_DUMMY", "CIB_CFG0", "CIB_CFG1", "CIB_CFG2", "CIB_CFG3"]

def main():
    pytrellis.load_database("../../../database")

    for dest in shared_tiles:
        dbcopy.dbcopy("MachXO2", "LCMXO2-1200HC", "CIB_CFG0", dest, copy_words=False, copy_enums=False, copy_conns=False)


if __name__ == "__main__":
    main()
