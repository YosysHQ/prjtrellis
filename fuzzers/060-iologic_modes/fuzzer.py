from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops

jobs = [
    {
        "cfg": FuzzConfig(job="IOLOGICL", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                          tiles=["MIB_R14C0:PICL0", "MIB_R15C0:PICL1", "MIB_R16C0:PICL2"]),
        "side": "L",
        "site": "IOL_L14A",
        "iol": "A"
    }
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
            return dict(loc=loc, mode=mode, program=program, comment=comment)

        cfg = job["cfg"]
        loc = job["site"]
        iol = job["iol"]
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "iologic.ncl"
        modes = ["NONE", "IREG_OREG", "IDDRX1_ODDRX1", "IDDRXN", "ODDRXN", "MIDDRX_MODDRX"]
        tie_program = ["LSRIMUX:0", "LSROMUX:0"]
        nonrouting.fuzz_enum_setting(cfg, "IOLOGIC{}.MODE".format(iol), modes,
                                     lambda x: get_substs(mode=x, program=["MODE:" + x] + tie_program), empty_bitfile, False)

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
