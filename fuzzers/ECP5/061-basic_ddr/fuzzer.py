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
]


def main():
    pytrellis.load_database("../../../database")
    pytrellis.load_database("../../../database")

    def per_job(job):
        def get_substs(ddrtype="", ddren="OFF", gsr="ENABLED", lsrimux="0", clkimux="CLK", lsromux="0", clkomux="CLK", lsrmux="LSR", datamux="PADDO"):
            if ddren == "ON":
                ddr = "{}:#ON ".format(ddrtype)
            else:
                ddr = ""
            if clkimux == "INV":
                clkimux = "CLK:::CLK=#INV"
            elif clkimux in ("0", "1"):
                clkimux = "1:::1={}".format(clkimux)
            if clkomux == "INV":
                clkomux = "CLK:::CLK=#INV"
            elif clkomux in ("0", "1"):
                clkomux = "1:::1={}".format(clkomux)
            if lsrmux == "INV":
                lsrmux = "LSR:::LSR=#INV"
            if side in ("T, B"):
                s = "S"
            else:
                s = ""
            return dict(loc=loc, ddr=ddr, gsr=gsr, lsrimux=lsrimux, clkimux=clkimux, lsromux=lsromux, clkomux=clkomux, lsrmux=lsrmux, s=s, pin=pin, datamux=datamux)

        cfg = job["cfg"]
        loc = job["site"]
        iol = job["iol"]
        side = job["side"]
        pin = job["pin"]

        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "iologic.ncl"

        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.IDDRX1".format(iol), ["OFF", "ON"],
                                     lambda x: get_substs(ddrtype="IDDRX1", ddren=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.ODDRX1".format(iol), ["OFF", "ON"],
                                     lambda x: get_substs(ddrtype="ODDRX1", ddren=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.GSR".format(iol), ["ENABLED", "DISABLED"],
                                     lambda x: get_substs(gsr=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.LSRIMUX".format(iol), ["LSRMUX", "0"],
                                     lambda x: get_substs(lsrimux=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.LSROMUX".format(iol), ["LSRMUX", "0"],
                                     lambda x: get_substs(lsromux=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.CLKIMUX".format(iol), ["CLK", "INV", "0"],
                                     lambda x: get_substs(clkimux=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.CLKOMUX".format(iol), ["CLK", "INV", "0"],
                                     lambda x: get_substs(clkomux=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.LSRMUX".format(iol), ["LSR", "INV"],
                                     lambda x: get_substs(lsrmux=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "PIO{}.DATAMUX_ODDR".format(iol), ["PADDO", "IOLDO"],
                                     lambda x: get_substs(datamux=x), empty_bitfile, False)
    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
