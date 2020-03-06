from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops


jobs = [
    {
        "cfg": FuzzConfig(job="IOLOGICLA", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C0:PICL0", "MIB_R15C0:PICL1", "MIB_R16C0:PICL2"]),
        "side": "L",
        "site": "IOL_L14A",
        "iol": "A",
        "pin": "A2"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICLB", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C0:PICL0", "MIB_R15C0:PICL1", "MIB_R16C0:PICL2"]),
        "side": "L",
        "site": "IOL_L14B",
        "iol": "B",
        "pin": "B1"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICLC", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C0:PICL0", "MIB_R15C0:PICL1", "MIB_R16C0:PICL2"]),
        "side": "L",
        "site": "IOL_L14C",
        "iol": "C",
        "pin": "B2"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICLD", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C0:PICL0", "MIB_R15C0:PICL1", "MIB_R16C0:PICL2"]),
        "side": "L",
        "site": "IOL_L14D",
        "iol": "D",
        "pin": "C2"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICRA", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C72:PICR0", "MIB_R15C72:PICR1", "MIB_R16C72:PICR2"]),
        "side": "R",
        "site": "IOL_R14A",
        "iol": "A",
        "pin": "C20"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICRB", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C72:PICR0", "MIB_R15C72:PICR1", "MIB_R16C72:PICR2"]),
        "side": "R",
        "site": "IOL_R14B",
        "iol": "B",
        "pin": "D19"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICRC", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C72:PICR0", "MIB_R15C72:PICR1", "MIB_R16C72:PICR2"]),
        "side": "R",
        "site": "IOL_R14C",
        "iol": "C",
        "pin": "D20"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICRD", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C72:PICR0", "MIB_R15C72:PICR1", "MIB_R16C72:PICR2"]),
        "side": "R",
        "site": "IOL_R14D",
        "iol": "D",
        "pin": "E19"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICTA", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R0C20:PIOT0", "MIB_R0C21:PIOT1", "MIB_R1C20:PICT0", "MIB_R1C21:PICT1"]),
        "side": "T",
        "site": "IOL_T20A",
        "iol": "A",
        "pin": "D9"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICTB", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R0C20:PIOT0", "MIB_R0C21:PIOT1", "MIB_R1C20:PICT0", "MIB_R1C21:PICT1"]),
        "side": "T",
        "site": "IOL_T20B",
        "iol": "B",
        "pin": "E9"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICBA", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R50C11:PICB0", "MIB_R50C12:PICB1"]),
        "side": "B",
        "site": "IOL_B11A",
        "iol": "A",
        "pin": "V2"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICBB", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R50C11:PICB0", "MIB_R50C12:PICB1"]),
        "side": "B",
        "site": "IOL_B11B",
        "iol": "B",
        "pin": "W2"
    },
]


def main():
    pytrellis.load_database("../../../database")
    pytrellis.load_database("../../../database")

    def per_job(job):
        def get_substs(regtype="", regen="OFF", regset="RESET", srmode="ASYNC", regmode="FF", cemux="CE", ceimux="1", ceomux="1", datamux="PADDO", trimux="PADDT"):
            clkimux = "CLK"
            clkomux = "CLK"
            if regen == "ON":
                reg = "{}:::REGSET={},{}REGMODE={}".format(regtype, regset, "IN" if regtype == "FF" else "OUT", regmode)
                if regmode == "LATCH":
                    if regtype == "FF":
                        clkimux = "CLK:::CLK=#INV" # clk is inverted for latches
                    else:
                        clkomux = "CLK:::CLK=#INV" # clk is inverted for latches
            else:
                reg = ""
            if side in ("T, B"):
                s = "S"
            else:
                s = ""
            if cemux == "INV":
                cemux = "CE:::CE=#INV"
            return dict(loc=loc, reg=reg, s=s, pin=pin, srmode=srmode, clkimux=clkimux, clkomux=clkomux, cemux=cemux, ceimux=ceimux, ceomux=ceomux, datamux=datamux, trimux=trimux)

        cfg = job["cfg"]
        loc = job["site"]
        iol = job["iol"]
        side = job["side"]
        pin = job["pin"]

        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "iologic.ncl"

        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.FF".format(iol), ["OFF", "ON"],
                                     lambda x: get_substs(regtype="FF", regen=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.FF.INREGMODE".format(iol), ["FF", "LATCH"],
                                     lambda x: get_substs(regtype="FF", regen="ON", regmode=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.FF.REGSET".format(iol), ["SET", "RESET"],
                                     lambda x: get_substs(regtype="FF", regen="ON", regset=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.OUTREG".format(iol), ["OFF", "ON"],
                                     lambda x: get_substs(regtype="OUTREG", regen=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.OUTREG.REGSET".format(iol), ["SET", "RESET"],
                                     lambda x: get_substs(regtype="OUTREG", regen="ON", regset=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.OUTREG.OUTREGMODE".format(iol), ["FF", "LATCH"],
                                     lambda x: get_substs(regtype="OUTREG", regen="ON", regmode=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.TSREG".format(iol), ["OFF", "ON"],
                                     lambda x: get_substs(regtype="TSREG", regen=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.TSREG.OUTREGMODE".format(iol), ["FF", "LATCH"],
                                     lambda x: get_substs(regtype="TSREG", regen="ON", regmode=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.TSREG.REGSET".format(iol), ["SET", "RESET"],
                                     lambda x: get_substs(regtype="TSREG", regen="ON", regset=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.SRMODE".format(iol), ["ASYNC", "LSR_OVER_CE"],
                                     lambda x: get_substs(srmode=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.CEIMUX".format(iol), ["CEMUX", "1"],
                                     lambda x: get_substs(ceimux=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.CEMUX".format(iol), ["CE", "INV"],
                                     lambda x: get_substs(cemux=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.CEOMUX".format(iol), ["CEMUX", "1"],
                                     lambda x: get_substs(ceomux=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "PIO{}.DATAMUX_OREG".format(iol), ["PADDO", "IOLDO"],
                                     lambda x: get_substs(datamux=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "PIO{}.TRIMUX_TSREG".format(iol), ["PADDT", "IOLTO"],
                                     lambda x: get_substs(trimux=x), empty_bitfile, False)
    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
