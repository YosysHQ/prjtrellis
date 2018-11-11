from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

jobs = [(FuzzConfig(job="LDQS17", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["MIB_R17C0:PICL0_DQS2", "MIB_R15C0:PICL1_DQS0", "MIB_R16C0:PICL2_DQS1",
                           "MIB_R18C0:PICL1_DQS3"]),
         "LDQS17", "R17C0"),
        (FuzzConfig(job="RDQS17", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                    tiles=["MIB_R17C90:PICR0_DQS2", "MIB_R15C90:PICR1_DQS0", "MIB_R16C90:PICR2_DQS1",
                           "MIB_R18C90:PICR1_DQS3"]),
         "RDQS17", "R17C90"),
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

        def get_substs(mode="DQSBUFM", program={}, ddrdel="DDRDEL", read="NO", rdloadn="NO", wrloadn="NO", pause="NO"):
            if mode == "NONE":
                comment = "//"
            else:
                comment = ""
            program = ",".join(["{}={}".format(k, v) for k, v in program.items()])
            ties = []
            if ddrdel != "DDRDEL":
                ties.append("DDRDEL={}".format(ddrdel))
            if read != "YES":
                ties.append("READ0=0")
                ties.append("READ1=0")
            if rdloadn != "YES":
                ties.append("RDLOADN=0")
            if wrloadn != "YES":
                ties.append("WRLOADN=0")
            if pause != "YES":
                ties.append("PAUSE=0")
            if len(ties) > 0:
                program += ":{}".format(",".join(ties))
            return dict(site=loc, comment=comment, program=program)

        cfg, loc, rc = job
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "dqsbuf.ncl"

        nonrouting.fuzz_enum_setting(cfg, "DQS.MODE", ["NONE", "DQSBUFM"],
                                     lambda x: get_substs(mode=x, program=dict(GSR="ENABLED")), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "DQS.GSR".format(loc), ["ENABLED", "DISABLED"],
                                     lambda x: get_substs(program=dict(GSR=x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "DQS.DQS_LI_DEL_ADJ".format(loc), ["PLUS", "MINUS"],
                                     lambda x: get_substs(program=dict(DQS_LI_DEL_ADJ=x, DQS_LI_DEL_VAL=(1 if x == "PLUS" else 255))), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "DQS.DQS_LO_DEL_ADJ".format(loc), ["PLUS", "MINUS"],
                                     lambda x: get_substs(program=dict(DQS_LO_DEL_ADJ=x, DQS_LO_DEL_VAL=(1 if x == "PLUS" else 255))), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "DQS.DQS_LI_DEL_VAL".format(loc), 8,
                                     lambda x: get_substs(program=dict(DQS_LI_DEL_VAL=todecstr(x))), empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "DQS.DQS_LO_DEL_VAL".format(loc), 8,
                                     lambda x: get_substs(program=dict(DQS_LO_DEL_VAL=todecstr(x))), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "DQS.DDRDEL".format(loc), ["DDRDEL", "0"],
                                     lambda x: get_substs(ddrdel=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "DQS.READ_USED".format(loc), ["NO", "YES"],
                                     lambda x: get_substs(read=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "DQS.RDLOADN_USED".format(loc), ["NO", "YES"],
                                     lambda x: get_substs(rdloadn=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "DQS.WRLOADN_USED".format(loc), ["NO", "YES"],
                                     lambda x: get_substs(wrloadn=x), empty_bitfile, False)
        nonrouting.fuzz_enum_setting(cfg, "DQS.PAUSE_USED".format(loc), ["NO", "YES"],
                                     lambda x: get_substs(pause=x), empty_bitfile, False)

        nets = [
            "{}_DQSECLK".format(rc),
            "{}_JRDDIRECTION_DQS".format(rc),
            "{}_JRDMOVE_DQS".format(rc),
            "{}_JRDLOADN_DQS".format(rc),
            "{}_JWRDIRECTION_DQS".format(rc),
            "{}_JWRMOVE_DQS".format(rc),
            "{}_JWRLOADN_DQS".format(rc),
            "{}_JRST_DQS".format(rc),
            "{}_JSCLK_DQS".format(rc),
            "{}_JDQSI_DQS".format(rc),
            "{}_JREAD0_DQS".format(rc),
            "{}_JREAD1_DQS".format(rc),

            "{}_JRDCFLAG_DQS".format(rc),
            "{}_JWRCFLAG_DQS".format(rc),
            "{}_JBURSTDET_DQS".format(rc),
            "{}_JDATAVALID_DQS".format(rc),
            "{}_JPAUSE_DQS".format(rc),
            "{}_DDRDEL_DQS".format(rc),
            "{}_ECLK_DQS".format(rc),
            "{}_JDQSR90_DQS".format(rc),
            "{}_JDQSW270_DQS".format(rc),
            "{}_JDQSW_DQS".format(rc),
            "{}_DDRDEL".format(rc),
        ]

        for i in range(8):
            nets.append("{}_JDYNDELAY{}_DQS".format(rc, i))
        for i in range(3):
            nets.append("{}_RDPNTR{}_DQS".format(rc, i))
            nets.append("{}_WRPNTR{}_DQS".format(rc, i))
            nets.append("{}_JREADCLKSEL{}_DQS".format(rc, i))
        for i in range(3):
            nets.append("{}_JREAD{}_DQS".format(rc, i))

        cfg.ncl = "dqsbuf_routing.ncl"
        interconnect.fuzz_interconnect_with_netnames(cfg, nets, bidir=True)

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
