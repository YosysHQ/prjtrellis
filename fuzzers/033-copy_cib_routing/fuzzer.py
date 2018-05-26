import dbcopy
import pytrellis


def main():
    pytrellis.load_database("../../database")
    dbcopy.dbcopy("ECP5", "LFE5U-25F", "CIB", "CIB_EBR")


if __name__ == "__main__":
    main()
