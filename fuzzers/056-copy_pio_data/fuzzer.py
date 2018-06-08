import dbcopy
import pytrellis


def main():
    pytrellis.load_database("../../database")
    copy_routing_rules = {
        "PICL0": ["PICL0_DQS2"],
        "PICL1": ["PICL1_DQS0", "PICL1_DQS3"],
        "PICL2": ["PICL2_DQS1", "MIB_CIB_LR"],
        "PICR0": ["PICR0_DQS2"],
        "PICR1": ["PICR1_DQS0", "PICR1_DQS3"],
        "PICR2": ["PICR2_DQS1", "MIB_CIB_LR_A"],
        "PICB0": ["EFB0_PICB0", "EFB2_PICB0"],
        "PICB1": ["EFB1_PICB1", "EFB3_PICB1"],
    }
    for src, dest_tiles in sorted(copy_routing_rules.items()):
        for dest in dest_tiles:
            dbcopy.dbcopy("ECP5", "LFE5U-25F", src, dest, copy_conns=True, copy_muxes=True, copy_enums=False,
                          copy_words=False)

    copy_config_rules = {
        "PICR0": ["PICR0_DQS2"],
        "PICR1": ["PICR1_DQS0", "PICR1_DQS3"],
        "PICR2": ["PICR2_DQS1"],
        "EFB2_PICB0": ["EFB0_PICB0"],
        "EFB3_PICB1": ["EFB1_PICB1"],
    }

    for src, dest_tiles in sorted(copy_config_rules.items()):
        for dest in dest_tiles:
            dbcopy.dbcopy("ECP5", "LFE5U-25F", src, dest, copy_conns=False, copy_muxes=False, copy_enums=True,
                          copy_words=True)


if __name__ == "__main__":
    main()
