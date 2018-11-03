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
        "iol": "A"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICLB", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C0:PICL0", "MIB_R15C0:PICL1", "MIB_R16C0:PICL2"]),
        "side": "L",
        "site": "IOL_L14B",
        "iol": "B"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICLC", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C0:PICL0", "MIB_R15C0:PICL1", "MIB_R16C0:PICL2"]),
        "side": "L",
        "site": "IOL_L14C",
        "iol": "C"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICLD", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C0:PICL0", "MIB_R15C0:PICL1", "MIB_R16C0:PICL2"]),
        "side": "L",
        "site": "IOL_L14D",
        "iol": "D"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICRA", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C72:PICR0", "MIB_R15C72:PICR1", "MIB_R16C72:PICR2"]),
        "side": "R",
        "site": "IOL_R14A",
        "iol": "A"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICRB", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C72:PICR0", "MIB_R15C72:PICR1", "MIB_R16C72:PICR2"]),
        "side": "R",
        "site": "IOL_R14B",
        "iol": "B"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICRC", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C72:PICR0", "MIB_R15C72:PICR1", "MIB_R16C72:PICR2"]),
        "side": "R",
        "site": "IOL_R14C",
        "iol": "C"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICRD", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C72:PICR0", "MIB_R15C72:PICR1", "MIB_R16C72:PICR2"]),
        "side": "R",
        "site": "IOL_R14D",
        "iol": "D"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICTA", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R0C20:PIOT0", "MIB_R0C21:PIOT1", "MIB_R1C20:PICT0", "MIB_R1C21:PICT1"]),
        "side": "T",
        "site": "IOL_T20A",
        "iol": "A"
    },
    {
        "cfg": FuzzConfig(job="IOLOGICTB", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R0C20:PIOT0", "MIB_R0C21:PIOT1", "MIB_R1C20:PICT0", "MIB_R1C21:PICT1"]),
        "side": "T",
        "site": "IOL_T20B",
        "iol": "B"
    },
]


def main():
    pytrellis.load_database("../../database")
    pytrellis.load_database("../../database")

    def per_job(job):
        def get_substs(mode="IREG_OREG", program=[]):
            if mode == "NONE":
                comment = "//"
                program = ""
            else:
                comment = ""
                program = "program " + "\n\t\t\t".join(['"' + _ + ' "' for _ in program])
            if side in ("T, B"):
                s = "S"
            else:
                s = ""
            return dict(loc=loc, mode=mode, program=program, comment=comment, s=s)

        cfg = job["cfg"]
        loc = job["site"]
        iol = job["iol"]
        side = job["side"]

        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "iologic.ncl"
        modes = ["NONE", "IREG_OREG", "IDDRX1_ODDRX1"]
        if side in ("L", "R"):
            modes += ["IDDRXN", "ODDRXN", "MIDDRX_MODDRX"]
        tie_program = ["LSRIMUX:0", "LSROMUX:0", "CLKIMUX:1:::1=0", "CLKOMUX:1:::1=0"]
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.MODE".format(iol), modes,
                                     lambda x: get_substs(mode=x, program=["MODE:" + x] + tie_program), empty_bitfile, False,
                                     opt_pref=["MIDDRX_MODDRX"])

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
