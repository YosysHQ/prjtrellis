import dbcopy
import pytrellis


def main():
    pytrellis.load_database("../../../database")
    # dbcopy.dbcopy("MachXO2", "LCMXO2-1200HC", "CIB_CFG0", "CIB_PIC_T0")
    dbcopy.dbcopy("MachXO2", "LCMXO2-1200HC", "CIB_CFG0", "CIB_PIC_T_DUMMY")


if __name__ == "__main__":
    main()
