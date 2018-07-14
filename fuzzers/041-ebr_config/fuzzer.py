from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops

jobs = [
    ("R25C22", "EBR0", FuzzConfig(job="EBROUTE0", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                  tiles=["MIB_R25C22:MIB_EBR0", "MIB_R25C23:MIB_EBR1"])),
    ("R25C24", "EBR1", FuzzConfig(job="EBROUTE1", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                  tiles=["MIB_R25C24:MIB_EBR2", "MIB_R25C25:MIB_EBR3", "MIB_R25C26:MIB_EBR4"])),
    ("R25C26", "EBR2", FuzzConfig(job="EBROUTE2", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                  tiles=["MIB_R25C26:MIB_EBR4", "MIB_R25C27:MIB_EBR5", "MIB_R25C28:MIB_EBR6"])),
    ("R25C28", "EBR3", FuzzConfig(job="EBROUTE3", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                  tiles=["MIB_R25C28:MIB_EBR6", "MIB_R25C29:MIB_EBR7", "MIB_R25C30:MIB_EBR8"])),

]


def main():
    pytrellis.load_database("../../database")

    def per_job(job):
        def get_substs(mode, settings):
            ebrloc = loc
            if mode == "NONE":
                # easier to move EBR out the way than remove it
                ebrloc = "R25C60"
                mode = "PDPW16KD"
            if mode == "PDPW16KD" and "DATA_WIDTH_R" not in settings:
                settings["DATA_WIDTH_R"] = "18"
            if mode == "PDPW16KD" and "DATA_WIDTH_W" not in settings:
                settings["DATA_WIDTH_W"] = "36"
            if mode == "PDPW16KD" and "CSDECODE_W" not in settings:
                settings["CSDECODE_W"] = "0b111"
            if mode == "PDPW16KD" and "CSDECODE_R" not in settings:
                settings["CSDECODE_R"] = "0b111"
            if mode == "DP16KD" and "CSDECODE_A" not in settings:
                settings["CSDECODE_A"] = "0b111"
            if mode == "DP16KD" and "CSDECODE_B" not in settings:
                settings["CSDECODE_B"] = "0b111"
            return dict(loc=ebrloc, mode=mode, settings=",".join(["{}={}".format(k, v) for k, v in settings.items()]))

        loc, ebr, cfg = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "ebr.ncl"

        nonrouting.fuzz_enum_setting(cfg, "{}.MODE".format(ebr), ["NONE", "PDPW16KD", "DP16KD"],
                                     lambda x: get_substs(mode=x, settings={"GSR": "ENABLED"}), empty_bitfile)

        nonrouting.fuzz_enum_setting(cfg, "{}.PDPW16KD.DATA_WIDTH_R".format(ebr), ["1", "2", "4", "9", "18", "36"],
                                     lambda x: get_substs(mode="PDPW16KD", settings={"DATA_WIDTH_R": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.DP16KD.DATA_WIDTH_A".format(ebr), ["1", "2", "4", "9", "18"],
                                     lambda x: get_substs(mode="DP16KD", settings={"DATA_WIDTH_A": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.DP16KD.DATA_WIDTH_B".format(ebr), ["1", "2", "4", "9", "18"],
                                     lambda x: get_substs(mode="DP16KD", settings={"DATA_WIDTH_B": x}), empty_bitfile)

        nonrouting.fuzz_enum_setting(cfg, "{}.REGMODE_A".format(ebr), ["NOREG", "OUTREG"],
                                     lambda x: get_substs(mode="DP16KD", settings={"REGMODE_A": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.REGMODE_B".format(ebr), ["NOREG", "OUTREG"],
                                     lambda x: get_substs(mode="DP16KD", settings={"REGMODE_B": x}), empty_bitfile)

        nonrouting.fuzz_enum_setting(cfg, "{}.DP16KD.WRITEMODE_A".format(ebr),
                                     ["NORMAL", "WRITETHROUGH", "READBEFOREWRITE"],
                                     lambda x: get_substs(mode="DP16KD", settings={"WRITEMODE_A": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.DP16KD.WRITEMODE_B".format(ebr),
                                     ["NORMAL", "WRITETHROUGH", "READBEFOREWRITE"],
                                     lambda x: get_substs(mode="DP16KD", settings={"WRITEMODE_B": x}), empty_bitfile)

        nonrouting.fuzz_enum_setting(cfg, "{}.GSR".format(ebr), ["ENABLED", "DISABLED"],
                                     lambda x: get_substs(mode="DP16KD", settings={"GSR": x}), empty_bitfile)

        nonrouting.fuzz_enum_setting(cfg, "{}.RESETMODE".format(ebr), ["SYNC", "ASYNC"],
                                     lambda x: get_substs(mode="DP16KD", settings={"RESETMODE": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.ASYNC_RESET_RELEASE".format(ebr), ["SYNC", "ASYNC"],
                                     lambda x: get_substs(mode="DP16KD", settings={"ASYNC_RESET_RELEASE": x}),
                                     empty_bitfile)

        def bitstr(x):
            return "0b" + "".join(["1" if z else "0" for z in x])

        nonrouting.fuzz_word_setting(cfg, "{}.CSDECODE_A".format(ebr), 3, lambda x: get_substs(mode="DP16KD", settings={
            "CSDECODE_A": bitstr(x)}), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.CSDECODE_B".format(ebr), 3, lambda x: get_substs(mode="DP16KD", settings={
            "CSDECODE_B": bitstr(x)}), empty_bitfile)

        nonrouting.fuzz_word_setting(cfg, "{}.WID".format(ebr), 9, lambda x: get_substs(mode="DP16KD", settings={
            "WID": bitstr(x)}), empty_bitfile)

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
