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
        "rc": "R14C0",
    },
    {
        "cfg": FuzzConfig(job="IOLOGICLB", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C0:PICL0", "MIB_R15C0:PICL1", "MIB_R16C0:PICL2"]),
        "side": "L",
        "site": "IOL_L14B",
        "iol": "B",
        "rc": "R14C0",
    },
    {
        "cfg": FuzzConfig(job="IOLOGICLC", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C0:PICL0", "MIB_R15C0:PICL1", "MIB_R16C0:PICL2"]),
        "side": "L",
        "site": "IOL_L14C",
        "iol": "C",
        "rc": "R14C0",
    },
    {
        "cfg": FuzzConfig(job="IOLOGICLD", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C0:PICL0", "MIB_R15C0:PICL1", "MIB_R16C0:PICL2"]),
        "side": "L",
        "site": "IOL_L14D",
        "iol": "D",
        "rc": "R14C0",
    },
    {
        "cfg": FuzzConfig(job="IOLOGICRA", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C72:PICR0", "MIB_R15C72:PICR1", "MIB_R16C72:PICR2"]),
        "side": "R",
        "site": "IOL_R14A",
        "iol": "A",
        "rc": "R14C72",
    },
    {
        "cfg": FuzzConfig(job="IOLOGICRB", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C72:PICR0", "MIB_R15C72:PICR1", "MIB_R16C72:PICR2"]),
        "side": "R",
        "site": "IOL_R14B",
        "iol": "B",
        "rc": "R14C72",
    },
    {
        "cfg": FuzzConfig(job="IOLOGICRC", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C72:PICR0", "MIB_R15C72:PICR1", "MIB_R16C72:PICR2"]),
        "side": "R",
        "site": "IOL_R14C",
        "iol": "C",
        "rc": "R14C72",
    },
    {
        "cfg": FuzzConfig(job="IOLOGICRD", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C72:PICR0", "MIB_R15C72:PICR1", "MIB_R16C72:PICR2"]),
        "side": "R",
        "site": "IOL_R14D",
        "iol": "D",
        "rc": "R14C72",
    },
    {
        "cfg": FuzzConfig(job="IOLOGICTA", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R0C20:PIOT0", "MIB_R0C21:PIOT1", "MIB_R1C20:PICT0", "MIB_R1C21:PICT1"]),
        "side": "T",
        "site": "IOL_T20A",
        "iol": "A",
        "rc": "R0C20",
    },
    {
        "cfg": FuzzConfig(job="IOLOGICTB", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R0C20:PIOT0", "MIB_R0C21:PIOT1", "MIB_R1C20:PICT0", "MIB_R1C21:PICT1"]),
        "side": "T",
        "site": "IOL_T20B",
        "iol": "B",
        "rc": "R0C20",
    },
]


def todecstr(x):
    res = 0
    for i in range(len(x)):
        if x[i]:
            res |= 1 << i
    return str(res)


def main():
    pytrellis.load_database("../../database")

    def per_job(job):
        def get_substs(mode="", settings={}, program={}, route=""):
            if mode == "" or mode == "NONE":
                delay = ""
            else:
                delay = ",".join(["DELAY:::DEL_MODE={}".format(mode)] + ["{}={}".format(k, v) for k, v in settings.items()])
            program = " ".join(["{}:{}".format(k, v) for k, v in program.items()])
            if side in ("T, B"):
                s = "S"
            else:
                s = ""
            if route != "":
                route = "route\n\t\t{}_IOLDO{}.{}_IOLDO{}_PIO,\n\t\t{}_IOLDOD{}_{}IOLOGIC.{}_IOLDO{};".format(
                    rc, iol, rc, iol, rc, iol, s, rc, iol
                )
            return dict(loc=loc, delay=delay, program=program, route=route, s=s)

        cfg = job["cfg"]
        loc = job["site"]
        iol = job["iol"]
        side = job["side"]
        rc = job["rc"]

        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "iologic.ncl"
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.DELAY.OUTDEL".format(iol), ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(route=(x if x != "DISABLED" else "")),
                                     empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.DELAY.WAIT_FOR_EDGE".format(iol), ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(mode="USER_DEFINED",
                                                          settings={"DEL_VALUE": 0, "WAIT_FOR_EDGE": x}),
                                     empty_bitfile, False)

        nonrouting.fuzz_word_setting(cfg, "IOLOGIC{}.DELAY.DEL_VALUE".format(iol), 7,
                                     lambda x: get_substs(mode="USER_DEFINED",
                                                          settings={"DEL_VALUE": todecstr(x),
                                                                    "WAIT_FOR_EDGE": "DISABLED"}),
                                     empty_bitfile)


    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
