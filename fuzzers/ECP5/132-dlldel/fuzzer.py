from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

jobs = [(FuzzConfig(job="TDLLDEL", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["MIB_R0C40:TMID_0", "MIB_R0C41:TMID_1"]),
         [("DLLDEL_00", "R0C39"), ("DLLDEL_01", "R0C40"), ("DLLDEL_10", "R0C41"), ("DLLDEL_11", "R0C42")]
         ),
        (FuzzConfig(job="LDLLDEL", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C2:ECLK_L", "MIB_R34C3:LMID_0"]),
         [("DLLDEL_61", "R36C0"), ("DLLDEL_60", "R35C0"), ("DLLDEL_71", "R34C0"), ("DLLDEL_70", "R33C0")]
         ),
        (FuzzConfig(job="RDLLDEL", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["CIB_R34C88:ECLK_R", "MIB_R34C87:RMID_0"]),
         [("DLLDEL_31", "R36C90"), ("DLLDEL_30", "R35C90"), ("DLLDEL_21", "R34C90"), ("DLLDEL_20", "R33C90")]
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
        cfg, locs = job
        cfg.setup()

        empty_bitfile = cfg.build_design(cfg.ncl, {})

        for loc, rc in locs:
            if loc == "DLLDEL_10":
                cfg.tiles = list(reversed(cfg.tiles))

            def get_substs(mode="DLLDELD", program={}, ddrdel="DDRDEL", loadn="NO"):
                if mode == "NONE":
                    comment = "//"
                else:
                    comment = ""
                program = ",".join(["{}={}".format(k, v) for k, v in program.items()])
                ties = []
                if ddrdel != "DDRDEL":
                    ties.append("DDRDEL={}".format(ddrdel))
                if loadn != "YES":
                    ties.append("LOADN=0")
                if len(ties) > 0:
                    program += ":{}".format(",".join(ties))
                return dict(site=loc, comment=comment, program=program)

            cfg.ncl = "dlldel.ncl"

            nonrouting.fuzz_enum_setting(cfg, "{}.MODE".format(loc), ["NONE", "DLLDELD"],
                                         lambda x: get_substs(mode=x, program=dict(DEL_ADJ="PLUS")), empty_bitfile, False)
            nonrouting.fuzz_enum_setting(cfg, "{}.DEL_ADJ".format(loc), ["PLUS", "MINUS"],
                                         lambda x: get_substs(
                                             program=dict(DEL_ADJ=x, DEL_VAL=(1 if x == "PLUS" else 255))),
                                         empty_bitfile)
            nonrouting.fuzz_word_setting(cfg, "{}.DEL_VAL".format(loc), 8,
                                         lambda x: get_substs(program=dict(DEL_VAL=todecstr(x))), empty_bitfile)
            nonrouting.fuzz_enum_setting(cfg, "{}.DDRDEL".format(loc), ["DDRDEL", "0"],
                                         lambda x: get_substs(ddrdel=x), empty_bitfile, False)
            nonrouting.fuzz_enum_setting(cfg, "{}.LOADN_USED".format(loc), ["NO", "YES"],
                                         lambda x: get_substs(loadn=x), empty_bitfile, False)

            nets = [
                "{}_JA_DLLDEL".format(rc),
                "{}_DDRDEL_DLLDEL".format(rc),
                "{}_DLLDEL".format(rc),
                "{}_DDRDEL".format(rc),
                "{}_JCFLAG_DLLDEL".format(rc),
                "{}_JLOADN_DLLDEL".format(rc),
                "{}_JMOVE_DLLDEL".format(rc),
                "{}_JDIRECTION_DLLDEL".format(rc),
                "{}_Z_DLLDEL".format(rc),
                "{}_JINCK".format(rc),
            ]

            cfg.ncl = "dlldel_routing.ncl"
            interconnect.fuzz_interconnect_with_netnames(cfg, nets, bidir=True)

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
