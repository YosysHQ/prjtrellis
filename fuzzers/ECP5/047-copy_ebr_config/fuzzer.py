import dbcopy
import pytrellis


def main():
    pytrellis.load_database("../../../database")
    copy_rules = {
        "MIB_EBR8": ["EBR_SPINE_UL0", "EBR_SPINE_UL1", "EBR_SPINE_UL2", "EBR_CMUX_UL",
                     "EBR_SPINE_UR0", "EBR_SPINE_UR1", "EBR_SPINE_UR2",
                     "EBR_SPINE_LL0", "EBR_SPINE_LL1", "EBR_SPINE_LL2", "EBR_CMUX_LL",
                     "EBR_SPINE_LR0", "EBR_SPINE_LR1", "EBR_SPINE_LR2", "EBR_CMUX_LL_25K"],
        "MIB_EBR0": ["EBR_CMUX_UR", "EBR_CMUX_LR", "EBR_CMUX_LR_25K"],
    }
    for src, dest_tiles in sorted(copy_rules.items()):
        for dest in dest_tiles:
            dbcopy.dbcopy("ECP5", "LFE5U-25F", src, dest, copy_conns=True, copy_muxes=True, copy_enums=True,
                          copy_words=True)

if __name__ == "__main__":
    main()
