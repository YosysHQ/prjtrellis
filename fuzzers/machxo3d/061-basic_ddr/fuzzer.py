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
            def get_substs(ddrtype="", ddren="OFF", gsr="ENABLED", lsrimux="0", clkimux="CLK", lsromux="0", clkomux="CLK", lsrmux="LSR", datamux="PADDO"):
                if ddren == "ON":
                    ddr = "{}:#ON ".format(ddrtype)
                else:
                    ddr = ""
                if clkimux == "INV":
                    clkimux = "CLK:::CLK=#INV"
                elif clkimux in ("0", "1"):
                    clkimux = "{}".format(clkimux)
                if clkomux == "INV":
                    clkomux = "CLK:::CLK=#INV"
                elif clkomux in ("0", "1"):
                    clkomux = "{}".format(clkomux)
                if lsrmux == "INV":
                    lsrmux = "LSR:::LSR=#INV"
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
                return dict(loc=loc, ddr=ddr, gsr=gsr, lsrimux=lsrimux, clkimux=clkimux, lsromux=lsromux, clkomux=clkomux, lsrmux=lsrmux, s=s, pin=pin, datamux=datamux)

            nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.CLKIMUX".format(iol), ["CLK", "INV", "0"],
                                        lambda x: get_substs(clkimux=x), empty_bitfile, False)
            nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.CLKOMUX".format(iol), ["CLK", "INV", "0"],
                                        lambda x: get_substs(clkomux=x), empty_bitfile, False)
            nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.LSRMUX".format(iol), ["LSR", "INV"],
                                        lambda x: get_substs(lsrmux=x), empty_bitfile, False)
            nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.LSRIMUX".format(iol), ["LSRMUX", "0"],
                                        lambda x: get_substs(lsrimux=x), empty_bitfile, False)
            nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.LSROMUX".format(iol), ["LSRMUX", "0"],
                                        lambda x: get_substs(lsromux=x), empty_bitfile, False)
            nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.GSR".format(iol), ["ENABLED", "DISABLED"],
                                        lambda x: get_substs(gsr=x), empty_bitfile, False)
            nonrouting.fuzz_enum_setting(cfg, "PIO{}.DATAMUX_ODDR".format(iol), ["PADDO", "IOLDO"],
                                        lambda x: get_substs(datamux=x), empty_bitfile, False)

        fuzzloops.parallel_foreach(sites, per_site)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Basic DDR Attributes Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
