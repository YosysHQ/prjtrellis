from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops

jobs = [
    ("LPLL", FuzzConfig(job="GPLL_L0", family="MachXO2", device="LCMXO2-7000HC", ncl="empty.ncl",
                           tiles=["PT1:GPLL_L0"])),
    ("RPLL", FuzzConfig(job="GPLL_R0", family="MachXO2", device="LCMXO2-7000HC", ncl="empty.ncl",
                           tiles=["PT41:GPLL_R0"])),
]

def b2d(word):
    res = 0
    for i in range(len(word)):
        if word[i]:
            res |= 1 << i
    return res

def main():
    pytrellis.load_database("../../../database")

    def per_job(job):
        def get_substs(settings, mode="EHXPLLJ"):
            if mode == "NONE":
                comment = "//"
            else:
                comment = ""
            return dict(loc=loc, settings=",".join(["{}={}".format(k, v) for k, v in settings.items()]),
                        comment=comment)

        loc, cfg = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "pllconfig.ncl"

        nonrouting.fuzz_enum_setting(cfg, "MODE", ["NONE", "EHXPLLJ"],
                                     lambda x: get_substs(settings={}, mode=x), empty_bitfile, False)

        nonrouting.fuzz_word_setting(cfg, "CLKI_DIV", 7, lambda x: get_substs(settings={"CLKI_DIV": b2d(x) + 1}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "CLKFB_DIV", 7, lambda x: get_substs(settings={"CLKFB_DIV": b2d(x) + 1}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "CLKOP_DIV", 7, lambda x: get_substs(settings={"CLKOP_DIV": b2d(x) + 1}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "CLKOS_DIV", 7, lambda x: get_substs(settings={"CLKOS_DIV": b2d(x) + 1}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "CLKOS2_DIV", 7, lambda x: get_substs(settings={"CLKOS2_DIV": b2d(x) + 1}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "CLKOS3_DIV", 7, lambda x: get_substs(settings={"CLKOS3_DIV": b2d(x) + 1}),
                                     empty_bitfile)

        nonrouting.fuzz_enum_setting(cfg, "CLOCK_ENABLE_PORTS", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"CLOCK_ENABLE_PORTS": x}), empty_bitfile, False)

        nonrouting.fuzz_enum_setting(cfg, "CLKOP_ENABLE", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"CLKOP_ENABLE": x}), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "CLKOS_ENABLE", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"CLKOS_ENABLE": x}), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "CLKOS2_ENABLE", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"CLKOS2_ENABLE": x}), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "CLKOS3_ENABLE", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"CLKOS3_ENABLE": x}), empty_bitfile, False)

        nonrouting.fuzz_enum_setting(cfg, "VCO_BYPASS_A0", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"VCO_BYPASS_A0": x}), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "VCO_BYPASS_B0", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"VCO_BYPASS_B0": x}), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "VCO_BYPASS_C0", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"VCO_BYPASS_C0": x}), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "VCO_BYPASS_D0", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"VCO_BYPASS_D0": x}), empty_bitfile, False)

        nonrouting.fuzz_word_setting(cfg, "CLKOP_CPHASE", 7, lambda x: get_substs(settings={"CLKOP_CPHASE": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "CLKOS_CPHASE", 7, lambda x: get_substs(settings={"CLKOS_CPHASE": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "CLKOS2_CPHASE", 7, lambda x: get_substs(settings={"CLKOS2_CPHASE": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "CLKOS3_CPHASE", 7, lambda x: get_substs(settings={"CLKOS3_CPHASE": b2d(x)}),
                                     empty_bitfile)

        nonrouting.fuzz_word_setting(cfg, "CLKOP_FPHASE", 3, lambda x: get_substs(settings={"CLKOP_FPHASE": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "CLKOS_FPHASE", 3, lambda x: get_substs(settings={"CLKOS_FPHASE": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "CLKOS2_FPHASE", 3, lambda x: get_substs(settings={"CLKOS2_FPHASE": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "CLKOS3_FPHASE", 3, lambda x: get_substs(settings={"CLKOS3_FPHASE": b2d(x)}),
                                     empty_bitfile)


        nonrouting.fuzz_enum_setting(cfg, "FEEDBK_PATH", ["CLKOP", "CLKOS", "CLKOS2", "CLKOS3", "INT_DIVA", "INT_DIVB", "INT_DIVC", "INT_DIVD", "USERCLOCK"],
                                     lambda x: get_substs(settings={"FEEDBK_PATH": x}), empty_bitfile, False)
        
        nonrouting.fuzz_word_setting(cfg, "KVCO", 3, lambda x: get_substs(settings={"KVCO": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "LPF_CAPACITOR", 2, lambda x: get_substs(settings={"LPF_CAPACITOR": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "LPF_RESISTOR", 7, lambda x: get_substs(settings={"LPF_RESISTOR": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "ICP_CURRENT", 5, lambda x: get_substs(settings={"ICP_CURRENT": b2d(x)}),
                                     empty_bitfile)

        nonrouting.fuzz_enum_setting(cfg, "FRACN_ENABLE", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"FRACN_ENABLE": x}), empty_bitfile, False)
        nonrouting.fuzz_word_setting(cfg, "FRACN_DIV", 16, lambda x: get_substs(settings={"FRACN_DIV": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "FRACN_ORDER", 2, lambda x: get_substs(settings={"FRACN_ORDER": b2d(x)}),
                                     empty_bitfile)

        nonrouting.fuzz_enum_setting(cfg, "CLKOP_TRIM_POL", ["RISING", "FALLING"],
                                     lambda x: get_substs(settings={"CLKOP_TRIM_POL": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "CLKOP_TRIM_DELAY", ["0", "1", "2", "4"],
                                     lambda x: get_substs(settings={"CLKOP_TRIM_DELAY": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "CLKOS_TRIM_POL", ["RISING", "FALLING"],
                                     lambda x: get_substs(settings={"CLKOS_TRIM_POL": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "CLKOS_TRIM_DELAY", ["0", "1", "2", "4"],
                                     lambda x: get_substs(settings={"CLKOS_TRIM_DELAY": x}), empty_bitfile)

        nonrouting.fuzz_enum_setting(cfg, "PLL_EXPERT", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"PLL_EXPERT": x}), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "PLL_USE_WB", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"PLL_USE_WB": x}), empty_bitfile, False)

        nonrouting.fuzz_word_setting(cfg, "PREDIVIDER_MUXA1", 2, lambda x: get_substs(settings={"PREDIVIDER_MUXA1": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "PREDIVIDER_MUXB1", 2, lambda x: get_substs(settings={"PREDIVIDER_MUXB1": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "PREDIVIDER_MUXC1", 2, lambda x: get_substs(settings={"PREDIVIDER_MUXC1": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "PREDIVIDER_MUXD1", 2, lambda x: get_substs(settings={"PREDIVIDER_MUXD1": b2d(x)}),
                                     empty_bitfile)

        nonrouting.fuzz_enum_setting(cfg, "OUTDIVIDER_MUXA2", ["DIVA", "REFCLK"],
                                     lambda x: get_substs(settings={"OUTDIVIDER_MUXA2": x}), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "OUTDIVIDER_MUXB2", ["DIVB", "REFCLK"],
                                     lambda x: get_substs(settings={"OUTDIVIDER_MUXB2": x}), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "OUTDIVIDER_MUXC2", ["DIVC", "REFCLK"],
                                     lambda x: get_substs(settings={"OUTDIVIDER_MUXC2": x}), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "OUTDIVIDER_MUXD2", ["DIVD", "REFCLK"],
                                     lambda x: get_substs(settings={"OUTDIVIDER_MUXD2": x}), empty_bitfile, False)

        nonrouting.fuzz_word_setting(cfg, "FREQ_LOCK_ACCURACY", 2, lambda x: get_substs(settings={"FREQ_LOCK_ACCURACY": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "PLL_LOCK_MODE", 3, lambda x: get_substs(settings={"PLL_LOCK_MODE": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "PLL_LOCK_DELAY", ["200", "400", "800", "1600"],
                                     lambda x: get_substs(settings={"PLL_LOCK_DELAY": x}), empty_bitfile)

        nonrouting.fuzz_word_setting(cfg, "GMC_GAIN", 3, lambda x: get_substs(settings={"GMC_GAIN": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "GMC_TEST", 4, lambda x: get_substs(settings={"GMC_TEST": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "MFG1_TEST", 3, lambda x: get_substs(settings={"MFG1_TEST": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "MFG2_TEST", 3, lambda x: get_substs(settings={"MFG2_TEST": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "MFG_FORCE_VFILTER", 1,
                                     lambda x: get_substs(settings={"MFG_FORCE_VFILTER": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "MFG_ICP_TEST", 1, lambda x: get_substs(settings={"MFG_ICP_TEST": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "MFG_EN_UP", 1, lambda x: get_substs(settings={"MFG_EN_UP": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "MFG_FLOAT_ICP", 1, lambda x: get_substs(settings={"MFG_FLOAT_ICP": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "MFG_GMC_PRESET", 1,
                                     lambda x: get_substs(settings={"MFG_GMC_PRESET": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "MFG_LF_PRESET", 1, lambda x: get_substs(settings={"MFG_LF_PRESET": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "MFG_GMC_RESET", 1, lambda x: get_substs(settings={"MFG_GMC_RESET": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "MFG_LF_RESET", 1, lambda x: get_substs(settings={"MFG_LF_RESET": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "MFG_LF_RESGRND", 1,
                                     lambda x: get_substs(settings={"MFG_LF_RESGRND": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "MFG_GMCREF_SEL", 2,
                                     lambda x: get_substs(settings={"MFG_GMCREF_SEL": b2d(x)}),
                                     empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "MFG_ENABLE_FILTEROPAMP", 1,
                                     lambda x: get_substs(settings={"MFG_EN_FILTEROPAMP": b2d(x)}),
                                     empty_bitfile)
        
        nonrouting.fuzz_enum_setting(cfg, "STDBY_ENABLE", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"STDBY_ENABLE": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "REFIN_RESET", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"REFIN_RESET": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "SYNC_ENABLE", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"SYNC_ENABLE": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "INT_LOCK_STICKY", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"INT_LOCK_STICKY": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "DPHASE_SOURCE", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"DPHASE_SOURCE": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "INTFB_WAKE", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"INTFB_WAKE": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "PLLRST_ENA", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"PLLRST_ENA": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "MRST_ENA", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"MRST_ENA": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "DCRST_ENA", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"DCRST_ENA": x}), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "DDRST_ENA", ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(settings={"DDRST_ENA": x}), empty_bitfile)

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
