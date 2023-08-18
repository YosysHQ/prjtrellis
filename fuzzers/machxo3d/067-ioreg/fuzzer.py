from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import argparse

jobs = [
    # 0
    {
        "cfg": FuzzConfig(job="IOLOGIC_L0", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty_9400.ncl",
                          tiles=["PL13:PIC_L0"]),
        "side": "L",
        "sites": [("IOL_L13A", "A", "G1"),("IOL_L13B", "B", "H2"),("IOL_L13C", "C", "H4"),("IOL_L13D", "D", "J6")],
        "ncl": "iologic_9400.ncl"
    },

    {
        "cfg": FuzzConfig(job="IOLOGIC_R1", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty_9400.ncl",
                          tiles=["PR16:PIC_R1"]),
        "side": "R",
        "sites": [("IOL_R16A", "A", "G16"),("IOL_R16B", "B", "H15"),("IOL_R16C", "C", "H13"),("IOL_R16D", "D", "J12")],
        "ncl": "iologic_9400.ncl"
    },

    {
        "cfg": FuzzConfig(job="IOLOGIC_T0", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty_9400.ncl",
                          tiles=["PT15:PIC_T0"]),
        "side": "T",
        "sites": [("IOL_T15A", "A", "D6"), ("IOL_T15B", "B", "E7"), ("IOL_T15C", "C", "C6"), ("IOL_T15D", "D", "A6")],
        "ncl": "iologic_9400.ncl"
    },
    {
        "cfg": FuzzConfig(job="IOLOGIC_B0", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty_9400.ncl",
                          tiles=["PB18:PIC_B0"]),
        "side": "B",
        "sites": [("IOL_B18A", "A", "R7"), ("IOL_B18B", "B", "P7"), ("IOL_B18C", "C", "M7"), ("IOL_B18D", "D", "N7")],
        "ncl": "iologic_9400.ncl"
    },
]

def main(args):
    pytrellis.load_database("../../../database")

    for job in [jobs[i] for i in args.ids]:

        cfg = job["cfg"]
        side = job["side"]
        sites = job["sites"]

        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = job["ncl"]

        def per_site(site):
            loc, iol, pin = site

            def get_substs(regtype="", regen="OFF", regset="RESET", srmode="ASYNC", regmode="FF", cemux="CE", ceimux="1", ceomux="1", datamux="PADDO", trimux="PADDT", tsmux="TS"):
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
                if side == "L":
                    s = ""
                else:
                    if iol in ("B", "D"):
                        s = ""
                    else:
                        if iol == "A":
                            s = side
                        else:
                            if side == "R":
                                s = side
                            else:
                                s = side + "S"
                if cemux == "INV":
                    cemux = "CE:::CE=#INV"
                if tsmux == "INV":
                    tsmux = "TS:::TS=#INV"
                return dict(loc=loc, reg=reg, s=s, pin=pin, srmode=srmode, clkimux=clkimux, clkomux=clkomux, cemux=cemux, ceimux=ceimux, ceomux=ceomux, datamux=datamux, trimux=trimux, tsmux=tsmux)

            nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.FF.INREGMODE".format(iol), ["FF", "LATCH"],
                                        lambda x: get_substs(regtype="FF", regen="ON", regmode=x), empty_bitfile, False)
            nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.FF.REGSET".format(iol), ["SET", "RESET"],
                                        lambda x: get_substs(regtype="FF", regen="ON", regset=x), empty_bitfile, False)
            nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.OUTREG.REGSET".format(iol), ["SET", "RESET"],
                                        lambda x: get_substs(regtype="OUTREG", regen="ON", regset=x), empty_bitfile, False)
            nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.OUTREG.OUTREGMODE".format(iol), ["FF", "LATCH"],
                                        lambda x: get_substs(regtype="OUTREG", regen="ON", regmode=x), empty_bitfile, False)
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
            nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.TSMUX".format(iol), ["TS", "INV"],
                                        lambda x: get_substs(tsmux=x), empty_bitfile, False)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.DATAMUX_OREG".format(iol), ["PADDO", "IOLDO"],
                                        lambda x: get_substs(datamux=x), empty_bitfile, False)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.TRIMUX_TSREG".format(iol), ["PADDT", "IOLTO"],
                                        lambda x: get_substs(trimux=x), empty_bitfile, False)

        fuzzloops.parallel_foreach(sites, per_site)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IO REG Attributes Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
