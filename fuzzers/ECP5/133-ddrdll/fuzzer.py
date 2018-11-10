from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

jobs = [(FuzzConfig(job="DDRDLL_TL", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["MIB_R10C2:DDRDLL_UL"]),
         "DDRDLL_TL", "R0C0"
         ),
        (FuzzConfig(job="DDRDLL_TR", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["MIB_R10C88:DDRDLL_UR"]),
         "DDRDLL_TR", "R0C90"
         ),
        (FuzzConfig(job="DDRDLL_BL", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["MIB_R58C2:DDRDLL_LL"]),
         "DDRDLL_BL", "R71C0"
         ),
        (FuzzConfig(job="DDRDLL_BR", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["MIB_R58C88:DDRDLL_LR"]),
         "DDRDLL_BR", "R71C90"
         ),

        (FuzzConfig(job="DDRDLL_TL_25k", family="ECP5", device="LFE5U-25F", ncl="empty_25k.ncl",
                    tiles=["MIB_R13C2:DDRDLL_ULA"]),
         "DDRDLL_TL", "R0C0"
         ),
        (FuzzConfig(job="DDRDLL_TR_25k", family="ECP5", device="LFE5U-25F", ncl="empty_25k.ncl",
                    tiles=["MIB_R13C70:DDRDLL_URA"]),
         "DDRDLL_TR", "R0C72"
         ),
        ]


def todecstr(x):
    res = 0
    for i in range(len(x)):
        if x[i]:
            res |= 1 << i
    return str(res)


def main():
    pytrellis.load_database("../../../database")

    def per_job(job):
        cfg, loc, rc = job
        cfg.setup()

        def get_substs(mode="DDRDLLA", program={}):
            if mode == "NONE":
                comment = "//"
            else:
                comment = ""
            program = ",".join(["{}={}".format(k, v) for k, v in program.items()])
            return dict(site=loc, comment=comment, program=program)

        empty_bitfile = cfg.build_design(cfg.ncl, {})
        if cfg.job.endswith("25k"):
            cfg.ncl = "ddrdll_25k.ncl"
        else:
            cfg.ncl = "ddrdll.ncl"

        nonrouting.fuzz_enum_setting(cfg, "DDRDLL.MODE", ["NONE", "DDRDLLA"],
                                     lambda x: get_substs(mode=x, program=dict(GSR="ENABLED", FORCE_MAX_DELAY=(
                                         "YES" if x.endswith("YES") else "NO"))), empty_bitfile, False,
                                     ignore_cover=["DDRDLLA_NO", "DDRDLLA_YES"])
        nonrouting.fuzz_enum_setting(cfg, "DDRDLL.GSR".format(loc), ["ENABLED", "DISABLED"],
                                     lambda x: get_substs(program=dict(GSR=x)), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "DDRDLL.FORCE_MAX_DELAY".format(loc), ["NO", "YES"],
                                     lambda x: get_substs(program=dict(FORCE_MAX_DELAY=x)), empty_bitfile, False)
        nets = [
            "{}_JCIBCLK0".format(rc),
            "{}_JDDRDLLCLK".format(rc),
            "{}_JCLK_DDRDLL".format(rc),
            "{}_JDIVOSC_DDRDLL".format(rc),
            "{}_JLOCK_DDRDLL".format(rc),
            "{}_DDRDEL_DDRDLL".format(rc),
            "{}_JFREEZE_DDRDLL".format(rc),
            "{}_JUDDCNTLN_DDRDLL".format(rc),
            "{}_JRST_DDRDLL".format(rc),
        ]
        for i in range(8):
            nets.append("{}_JDCNTL{}_DDRDLL".format(rc, i))
        if cfg.job.endswith("25k"):
            cfg.ncl = "ddrdll_routing_25k.ncl"
        else:
            cfg.ncl = "ddrdll_routing.ncl"
        interconnect.fuzz_interconnect_with_netnames(cfg, nets, bidir=True)

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
