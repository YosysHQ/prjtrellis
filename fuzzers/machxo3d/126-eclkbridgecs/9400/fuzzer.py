from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops

jobs = [(FuzzConfig(job="ECLKBRIDGECS1", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty.ncl",
                    tiles=["CENTER15:CENTER_EBR_CIB_10K"]), "ECLKBRIDGECS1"),
        (FuzzConfig(job="ECLKBRIDGECS0", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty.ncl",
                    tiles=["CENTER15:CENTER_EBR_CIB_10K"]), "ECLKBRIDGECS0")
        ]


def main():
    pytrellis.load_database("../../../../database")

    def per_job(job):

        def get_substs(mode="ECLKBRIDGECS"):
            if mode == "NONE":
                comment = "//"
            else:
                comment = ""
            return dict(site=loc, comment=comment)

        cfg, loc = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "eclkbridge.ncl"

        nonrouting.fuzz_enum_setting(cfg, "{}.MODE".format(loc), ["NONE", "ECLKBRIDGECS"],
                                     lambda x: get_substs(mode=x), empty_bitfile, False)



    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
