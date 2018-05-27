import dbcopy
import pytrellis

cib_tiles = ["CIB", "CIB_DSP", "CIB_EFB0", "CIB_EFB1", "CIB_LR", "CIB_LR_S", "CIB_PLL0", "CIB_PLL1", "CIB_PLL2",
             "CIB_PLL3", "VCIB_DCU0", "VCIB_DCU1", "VCIB_DCU2", "VCIB_DCU3", "VCIB_DCUA", "VCIB_DCUB", "VCIB_DCUC",
             "VCIB_DCUD", "VCIB_DCUF", "VCIB_DCUG", "VCIB_DCUH", "VCIB_DCUI"]


def main():
    pytrellis.load_database("../../database")
    for dest in cib_tiles:
        dbcopy.dbcopy("ECP5", "LFE5U-25F", "CIB_EBR", dest)


if __name__ == "__main__":
    main()
