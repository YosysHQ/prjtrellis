import dbcopy
import pytrellis

def main():
    pytrellis.load_database("../../database")
    dbcopy.dbcopy("ECP5", "LFE5U-25F", "BMID_0V", "BMID_0H")
    dbcopy.dbcopy("ECP5", "LFE5U-25F", "BMID_2V", "BMID_2")


if __name__ == "__main__":
    main()
