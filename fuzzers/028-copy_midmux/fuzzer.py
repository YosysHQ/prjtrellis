import dbcopy
import pytrellis

def main():
    pytrellis.load_database("../../database")
    dbcopy.dbcopy("ECP5", "LFE5U-25F", "BMID_0V", "BMID_0H", copy_enums=True, copy_words=True)
    dbcopy.dbcopy("ECP5", "LFE5U-25F", "BMID_2V", "BMID_2", copy_enums=True, copy_words=True)


if __name__ == "__main__":
    main()
