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
]


def main():
    pytrellis.load_database("../../database")

    def per_job(job):
        def get_substs(type, mode, value="", datamux="PADDO"):
            if "." in mode:
                program = "{}:::DDRMODE={},{}={}".format(type, mode.split(".")[0], mode.split(".")[1], value)
            elif "WRCLKMUX" in mode:
                program = "{}:{}".format(mode, value)
            elif mode != "NONE":
                program = "{}:::DDRMODE={}".format(type, mode)
            else:
                program = ""
            return dict(loc=loc, program=program, pin=pin, datamux=datamux)

        cfg = job["cfg"]
        loc = job["site"]
        iol = job["iol"]
        side = job["side"]
        pin = job["pin"]

        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "iologic.ncl"

        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.MIDDRX.MODE".format(iol), ["NONE", "MIDDRX2"],
                                     lambda x: get_substs(type="MIDDRX", mode=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.MODDRX.MODE".format(iol), ["NONE", "MODDRX2", "MOSHX2"],
                                     lambda x: get_substs(type="MODDRX", mode=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.MTDDRX.MODE".format(iol), ["NONE", "MTSHX2"],
                                     lambda x: get_substs(type="MTDDRX", mode=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.MTDDRX.DQSW_INVERT".format(iol), ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(type="MTDDRX", mode="MTSHX2.DQSW_INVERT", value=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.MIDDRX_MODDRX.WRCLKMUX".format(iol), ["DQSW", "DQSW270"],
                                     lambda x: get_substs(type="MODDRX", mode="WRCLKMUX", value=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "PIO{}.DATAMUX_MDDR".format(iol), ["PADDO", "IOLDO"],
                                     lambda x: get_substs(type="MODDRX", mode="MODDRX2", datamux=x), empty_bitfile, False)
    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
