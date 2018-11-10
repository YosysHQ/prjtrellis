import dbcopy
import pytrellis


def main():
    pytrellis.load_database("../../../database")
    copy_rules = {
        "MIB_DSP8": ["DSP_SPINE_UL0", "DSP_SPINE_UR0", "DSP_SPINE_UR1"],
    }
    for src, dest_tiles in sorted(copy_rules.items()):
        for dest in dest_tiles:
            dbcopy.dbcopy("ECP5", "LFE5U-25F", src, dest, copy_conns=True, copy_muxes=True, copy_enums=True,
                          copy_words=True)

if __name__ == "__main__":
    main()
