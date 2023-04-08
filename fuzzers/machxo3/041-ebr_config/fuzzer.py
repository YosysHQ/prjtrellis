from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops

jobs = [
    ("R6C17", "EBR0", FuzzConfig(job="EBROUTE0", family="MachXO3", device="LCMXO3LF-1300E", ncl="empty.ncl",
                                 tiles=["EBR_R6C17:EBR0", "EBR_R6C18:EBR1", "EBR_R6C19:EBR2"])),
]


def main():
    pytrellis.load_database("../../../database")

    def per_job(job):
        def get_substs(mode, settings):
            ebrloc = loc
            if mode == "NONE":
                # easier to move EBR out the way than remove it
                ebrloc = "R6C20"
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

        # in EBR0, for MODE just F1B8 needs to be left
        nonrouting.fuzz_enum_setting(cfg, "{}.MODE".format(ebr), ["PDPW8KC", "DP8KC", "FIFO8KB", "NONE"],
                                     lambda x: get_substs(mode=x, settings={"GSR": "ENABLED"}), empty_bitfile, False)

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

        nonrouting.fuzz_word_setting(cfg, "{}.WID".format(ebr), 10, lambda x: get_substs(mode="DP8KC", settings={
            "WID": bitstr(x)}), empty_bitfile)

        nonrouting.fuzz_word_setting(cfg, "{}.CSDECODE_A".format(ebr), 3, lambda x: get_substs(mode="DP8KC", settings={
            "CSDECODE_A": bitstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.CSDECODE_B".format(ebr), 3, lambda x: get_substs(mode="DP8KC", settings={
            "CSDECODE_B": bitstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.CSDECODE_W".format(ebr), 2, lambda x: get_substs(mode="FIFO8KB", settings={
            "CSDECODE_W": bitstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.CSDECODE_R".format(ebr), 2, lambda x: get_substs(mode="FIFO8KB", settings={
            "CSDECODE_R": bitstr(x)}), empty_bitfile)

        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.AEPOINTER".format(ebr), 14, lambda x: get_substs(mode="FIFO8KB", settings={
            "AEPOINTER": bitstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.AEPOINTER1".format(ebr), 14, lambda x: get_substs(mode="FIFO8KB", settings={
            "AEPOINTER1": bitstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.AFPOINTER".format(ebr), 14, lambda x: get_substs(mode="FIFO8KB", settings={
            "AFPOINTER": bitstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.AFPOINTER1".format(ebr), 14, lambda x: get_substs(mode="FIFO8KB", settings={
            "AFPOINTER1": bitstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.FULLPOINTER".format(ebr), 14, lambda x: get_substs(mode="FIFO8KB", settings={
            "FULLPOINTER": bitstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.FIFO8KB.FULLPOINTER1".format(ebr), 14, lambda x: get_substs(mode="FIFO8KB", settings={
            "FULLPOINTER1": bitstr(x)}), empty_bitfile)

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()