from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

jobs = [(FuzzConfig(job="PCSCLKDIV0", family="ECP5", device="LFE5UM5G-45F", ncl="empty.ncl",
                 tiles=["MIB_R71C40:BMID_0H", "MIB_R71C41:BMID_2"]), "PCSCLKDIV0", "R70C40"),
       (FuzzConfig(job="PCSCLKDIV1", family="ECP5", device="LFE5UM5G-45F", ncl="empty.ncl",
                 tiles=["MIB_R71C40:BMID_0H", "MIB_R71C41:BMID_2"]), "PCSCLKDIV1", "R70C40")]


def main():
    pytrellis.load_database("../../../database")

    def per_job(job):
        def get_substs(mode="PCSCLKDIV", program=None):
            if mode == "NONE":
                comment = "//"
            else:
                comment = ""
            if program is not None:
                program = ":::" + ",".join(["{}={}".format(k, v) for k, v in program.items()])
            else:
                program = ":#ON"
            return dict(loc=loc, comment=comment, program=program)
        cfg, loc, rc = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "pcsclkdiv.ncl"

        nonrouting.fuzz_enum_setting(cfg, "{}.MODE".format(loc), ["NONE", "PCSCLKDIV"],
                                     lambda x: get_substs(mode=x, program={"GSR": "ENABLED"}), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "{}.GSR".format(loc), ["DISABLED", "ENABLED"],
                                     lambda x: get_substs(program={"GSR": x}), empty_bitfile, False)
        cfg.ncl = "pcsclkdiv_routing.ncl"
        nets = [
            "{}_JRST_{}".format(rc, loc),
            "{}_JSEL2_{}".format(rc, loc),
            "{}_JSEL1_{}".format(rc, loc),
            "{}_JSEL0_{}".format(rc, loc),
            "{}_CDIV1_{}".format(rc, loc),
            "{}_CDIVX_{}".format(rc, loc),
            "{}_CLKI_{}".format(rc, loc),
            "{}_PCSCDIVI{}".format(rc, loc[-1]),
            "{}_JPCSCDIVCIB{}".format(rc, loc[-1]),
        ]
        interconnect.fuzz_interconnect_with_netnames(
            cfg,
            nets,
            bidir=True,
        )
    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
