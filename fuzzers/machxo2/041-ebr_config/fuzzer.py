from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops

jobs = [
    ("R6C17", "EBR", FuzzConfig(job="EBROUTE0", family="MachXO2", device="LCMXO2-1200HC", ncl="empty.ncl",
                                tiles=["EBR_R6C17:EBR0", "EBR_R6C18:EBR1", "EBR_R6C19:EBR2"])),
    ("R6C1", "EBR", FuzzConfig(job="EBROUTE0", family="MachXO2", device="LCMXO2-1200HC", ncl="empty.ncl",
                                tiles=["EBR_R6C1:EBR0_END"])),
]


def main():
    pytrellis.load_database("../../../database")

    for job in jobs:
        def get_substs(mode, settings):
            ebrloc = loc
            if mode == "NONE":
                # easier to move EBR out the way than remove it
                ebrloc = "R6C10"
                mode = "PDPW8KC"
            if mode == "PDPW8KC" and "DATA_WIDTH_R" not in settings:
                settings["DATA_WIDTH_R"] = "9"
            if mode == "PDPW8KC" and "DATA_WIDTH_W" not in settings:
                settings["DATA_WIDTH_W"] = "18"
            if mode == "PDPW8KC" and "CSDECODE_W" not in settings:
                settings["CSDECODE_W"] = "0b111"
            if mode == "PDPW8KC" and "CSDECODE_R" not in settings:
                settings["CSDECODE_R"] = "0b111"
            if mode == "DP8KC" and "CSDECODE_A" not in settings:
                settings["CSDECODE_A"] = "0b111"
            if mode == "DP8KC" and "CSDECODE_B" not in settings:
                settings["CSDECODE_B"] = "0b111"
            if mode == "FIFO8KB" and "DATA_WIDTH_R" not in settings:
                settings["DATA_WIDTH_R"] = "9"
            if mode == "FIFO8KB" and "DATA_WIDTH_W" not in settings:
                settings["DATA_WIDTH_W"] = "9"
            if mode == "FIFO8KB" and "CSDECODE_W" not in settings:
                settings["CSDECODE_W"] = "0b11"
            if mode == "FIFO8KB" and "CSDECODE_R" not in settings:
                settings["CSDECODE_R"] = "0b11"
            if mode == "FIFO8KB" and "RESETMODE" not in settings:
                settings["RESETMODE"] = "SYNC:EMPTYI=#INV,FULLI=#INV"
            return dict(loc=ebrloc, mode=mode, settings=",".join(["{}={}".format(k, v) for k, v in settings.items()]))

        loc, ebr, cfg = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "ebr.ncl"

        # in EBR0, for MODE just F1B8 needs to be left, in EBR1 remove F0B25
        nonrouting.fuzz_enum_setting(cfg, "{}.MODE".format(ebr), ["PDPW8KC", "DP8KC", "FIFO8KB", "NONE"],
                                     lambda x: get_substs(mode=x, settings={"GSR": "ENABLED"}), empty_bitfile, False,
                                     ignore_bits=([("EBR_R6C18:EBR1", 0, 25), 
                                     ("EBR_R6C17:EBR0", 1, 2),("EBR_R6C17:EBR0", 1, 3),("EBR_R6C17:EBR0", 1, 4),("EBR_R6C17:EBR0", 1, 13),
                                     ("EBR_R6C1:EBR0_END", 1, 13),("EBR_R6C1:EBR0_END", 1, 14),("EBR_R6C1:EBR0_END", 1, 15),("EBR_R6C1:EBR0_END", 1, 24) ]))
        nonrouting.fuzz_enum_setting(cfg, "{}.PDPW8KC.DATA_WIDTH_R".format(ebr), ["1", "2", "4", "9", "18"],
                                     lambda x: get_substs(mode="PDPW8KC", settings={"DATA_WIDTH_R": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.FIFO8KB.DATA_WIDTH_R".format(ebr), ["1", "2", "4", "9", "18"],
                                     lambda x: get_substs(mode="FIFO8KB", settings={"DATA_WIDTH_R": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.FIFO8KB.DATA_WIDTH_W".format(ebr), ["1", "2", "4", "9", "18"],
                                     lambda x: get_substs(mode="FIFO8KB", settings={"DATA_WIDTH_W": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.DP8KC.DATA_WIDTH_A".format(ebr), ["1", "2", "4", "9"],
                                     lambda x: get_substs(mode="DP8KC", settings={"DATA_WIDTH_A": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.DP8KC.DATA_WIDTH_B".format(ebr), ["1", "2", "4", "9"],
                                     lambda x: get_substs(mode="DP8KC", settings={"DATA_WIDTH_B": x}), empty_bitfile)


        nonrouting.fuzz_enum_setting(cfg, "{}.REGMODE_A".format(ebr), ["NOREG", "OUTREG"],
                                     lambda x: get_substs(mode="DP8KC", settings={"REGMODE_A": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.REGMODE_B".format(ebr), ["NOREG", "OUTREG"],
                                     lambda x: get_substs(mode="DP8KC", settings={"REGMODE_B": x}), empty_bitfile)

        nonrouting.fuzz_enum_setting(cfg, "{}.DP8KC.WRITEMODE_A".format(ebr),
                                     ["WRITETHROUGH", "READBEFOREWRITE", "NORMAL"],
                                     lambda x: get_substs(mode="DP8KC", settings={"WRITEMODE_A": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.DP8KC.WRITEMODE_B".format(ebr),
                                     ["WRITETHROUGH", "READBEFOREWRITE", "NORMAL"],
                                     lambda x: get_substs(mode="DP8KC", settings={"WRITEMODE_B": x}), empty_bitfile)

        nonrouting.fuzz_enum_setting(cfg, "{}.GSR".format(ebr), ["ENABLED", "DISABLED"],
                                     lambda x: get_substs(mode="DP8KC", settings={"GSR": x}), empty_bitfile)

        nonrouting.fuzz_enum_setting(cfg, "{}.RESETMODE".format(ebr), ["SYNC", "ASYNC"],
                                     lambda x: get_substs(mode="DP8KC", settings={"RESETMODE": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.ASYNC_RESET_RELEASE".format(ebr), ["SYNC", "ASYNC"],
                                     lambda x: get_substs(mode="DP8KC", settings={"ASYNC_RESET_RELEASE": x}),
                                     empty_bitfile)


        def bitstr(x):
           return "0b" + "".join(["1" if z else "0" for z in x])

        def tobinstr(x):
            return "0b" + "".join(reversed(["1" if x else "0" for x in  x]))
        def tobinstr_zero(x):
            return "0b0" + "".join(reversed(["1" if x else "0" for x in  x]))

        # must be size 10, but leading zero
        nonrouting.fuzz_word_setting(cfg, "{}.WID".format(ebr), 9, lambda x: get_substs(mode="DP8KC", settings={
            "WID": tobinstr_zero(x)}), empty_bitfile)
        #nonrouting.fuzz_word_setting(cfg, "{}.RID".format(ebr), 9, lambda x: get_substs(mode="DP8KC", settings={
        #    "RID": tobinstr_zero(x)}), empty_bitfile)


        nonrouting.fuzz_word_setting(cfg, "{}.CSDECODE_A".format(ebr), 3, lambda x: get_substs(mode="DP8KC", settings={
            "CSDECODE_A": bitstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.CSDECODE_B".format(ebr), 3, lambda x: get_substs(mode="DP8KC", settings={
            "CSDECODE_B": bitstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.CSDECODE_W".format(ebr), 2, lambda x: get_substs(mode="FIFO8KB", settings={
            "CSDECODE_W": bitstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.CSDECODE_R".format(ebr), 2, lambda x: get_substs(mode="FIFO8KB", settings={
            "CSDECODE_R": bitstr(x)}), empty_bitfile)

        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.AEPOINTER".format(ebr), 14, lambda x: get_substs(mode="FIFO8KB", settings={
            "AEPOINTER": tobinstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.AEPOINTER1".format(ebr), 14, lambda x: get_substs(mode="FIFO8KB", settings={
            "AEPOINTER1": tobinstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.AFPOINTER".format(ebr), 14, lambda x: get_substs(mode="FIFO8KB", settings={
            "AFPOINTER": tobinstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.AFPOINTER1".format(ebr), 14, lambda x: get_substs(mode="FIFO8KB", settings={
            "AFPOINTER1": tobinstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.FULLPOINTER".format(ebr), 14, lambda x: get_substs(mode="FIFO8KB", settings={
            "FULLPOINTER": tobinstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.FULLPOINTER1".format(ebr), 14, lambda x: get_substs(mode="FIFO8KB", settings={
            "FULLPOINTER1": tobinstr(x)}), empty_bitfile)

if __name__ == "__main__":
    main()
