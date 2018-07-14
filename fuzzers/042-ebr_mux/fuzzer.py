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
        def get_substs(mode, settings, muxes = None):
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
            setting_text = ",".join(["{}={}".format(k, v) for k, v in settings.items()])
            if muxes is not None:
                setting_text += ":" + ",".join(["{}={}".format(k, v) for k, v in muxes.items()])
            return dict(loc=ebrloc, mode=mode, settings=setting_text)

        def get_muxval(sig, val):
            if val == sig:
                return None
            elif val == "INV":
                return {sig: "#INV"}
            else:
                assert False
        loc, ebr, cfg = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "ebr.ncl"

        nonrouting.fuzz_enum_setting(cfg, "{}.CLKAMUX".format(ebr), ["CLKA", "INV"],
                                     lambda x: get_substs("DP16KD", {}, get_muxval("CLKA", x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.CLKBMUX".format(ebr), ["CLKB", "INV"],
                                     lambda x: get_substs("DP16KD", {}, get_muxval("CLKB", x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.RSTAMUX".format(ebr), ["RSTA", "INV"],
                                     lambda x: get_substs("DP16KD", {}, get_muxval("RSTA", x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.RSTBMUX".format(ebr), ["RSTB", "INV"],
                                     lambda x: get_substs("DP16KD", {}, get_muxval("RSTB", x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.OCEAMUX".format(ebr), ["OCEA", "INV"],
                                     lambda x: get_substs("DP16KD", {}, get_muxval("OCEA", x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.OCEBMUX".format(ebr), ["OCEB", "INV"],
                                     lambda x: get_substs("DP16KD", {}, get_muxval("OCEB", x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.WEAMUX".format(ebr), ["WEA", "INV"],
                                     lambda x: get_substs("DP16KD", {}, get_muxval("WEA", x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.WEBMUX".format(ebr), ["WEB", "INV"],
                                     lambda x: get_substs("DP16KD", {}, get_muxval("WEB", x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.CEAMUX".format(ebr), ["CEA", "INV"],
                                     lambda x: get_substs("DP16KD", {}, get_muxval("CEA", x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.CEBMUX".format(ebr), ["CEB", "INV"],
                                     lambda x: get_substs("DP16KD", {}, get_muxval("CEB", x)), empty_bitfile)
        for p in ("A", "B"):
            for i in range(4 if p == "A" else 2):
                sig = "AD{}{}".format(p, i)
                nonrouting.fuzz_enum_setting(cfg, "{}.{}MUX".format(ebr, sig), [sig, "INV"],
                                         lambda x: get_substs("DP16KD", {}, get_muxval(sig, x)), empty_bitfile)
    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
