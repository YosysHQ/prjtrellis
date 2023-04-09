import dbcopy
import pytrellis


def main():
    pytrellis.load_database("../../../database")
    copy_rules = {
        "EBR0": ["EBR0_10K"],
        "EBR0_END": ["EBR0_END_10K"],
        "EBR1": ["EBR1_10K"],
        "EBR2": ["EBR2_END", "EBR2_10K", "EBR2_END_10K"],
    }
    for src, dest_tiles in sorted(copy_rules.items()):
        for dest in dest_tiles:
            dbcopy.dbcopy("MachXO3", "LCMXO3LF-1300E", src, dest, copy_conns=True, copy_muxes=True, copy_enums=True,
                          copy_words=True)

if __name__ == "__main__":
    main()
