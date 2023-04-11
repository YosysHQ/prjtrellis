from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

jobs = [
        (FuzzConfig(job="TECLKSYNC0", family="MachXO3", device="LCMXO3LF-1300E", ncl="empty.ncl",
                    tiles=["PT13:PIC_T_DUMMY_VIQ"]), "TECLKSYNC0"),
        (FuzzConfig(job="TECLKSYNC1", family="MachXO3", device="LCMXO3LF-1300E", ncl="empty.ncl",
                    tiles=["PT13:PIC_T_DUMMY_VIQ"]), "TECLKSYNC1"),
        (FuzzConfig(job="BECLKSYNC0", family="MachXO3", device="LCMXO3LF-1300E", ncl="empty.ncl",
                    tiles=["PB13:PIC_B_DUMMY_VIQ"]), "BECLKSYNC0"),
        (FuzzConfig(job="BECLKSYNC1", family="MachXO3", device="LCMXO3LF-1300E", ncl="empty.ncl",
                    tiles=["PB13:PIC_B_DUMMY_VIQ"]), "BECLKSYNC1"),
        ]


def main():
    pytrellis.load_database("../../../../database")

    def per_job(job):

        def get_substs(mode="ECLKSYNCA"):
            if mode == "NONE":
                comment = "//"
            else:
                comment = ""
            return dict(site=loc, comment=comment)

        cfg, loc = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "eclksync.ncl"

        nonrouting.fuzz_enum_setting(cfg, "{}.MODE".format(loc), ["NONE", "ECLKSYNCA"],
                                     lambda x: get_substs(mode=x), empty_bitfile, False)



    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
