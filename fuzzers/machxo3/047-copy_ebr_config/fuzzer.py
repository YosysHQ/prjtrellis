import dbcopy
import pytrellis

def include_ebr_enum(conn):
    if isinstance(conn, pytrellis.EnumSettingBits):
        name = conn.name
    else:
        name = ""
    if name.startswith("EBR."):
        return True
    return False


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


    cib_copy_rules = {
        "CIB_EBR0": ["CIB_EBR0_10K"],
        "CIB_EBR1": ["CIB_EBR1_10K"],
        "CIB_EBR2": ["CIB_EBR2_10K"],
        "CIB_EBR0_END0": ["CIB_EBR0_END0_10K", "CIB_EBR0_END0_DLL3", "CIB_EBR0_END0_DLL5", "CIB_EBR0_END1", "CIB_EBR0_END2_DLL3", "CIB_EBR0_END2_DLL45"],
        "CIB_EBR2_END0": ["CIB_EBR2_END1", "CIB_EBR2_END1_10K", "CIB_EBR2_END1_SP"],
    }

    for src, dest_tiles in sorted(cib_copy_rules.items()):
        for dest in dest_tiles:
            dbcopy.copy_enums_with_predicate("MachXO3", "LCMXO3LF-1300E", src, dest, include_ebr_enum)

if __name__ == "__main__":
    main()
