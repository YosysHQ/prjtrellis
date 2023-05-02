from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

jobs = [
        (FuzzConfig(job="TDLLDEL", family="MachXO3", device="LCMXO3LF-9400C", ncl="empty.ncl",
                    tiles=["PT25:PIC_T_DUMMY_VIQ"]), [("TDLLDEL0", "R0C25"), ("TDLLDEL1", "R0C25")]),
        (FuzzConfig(job="BDLLDEL", family="MachXO3", device="LCMXO3LF-9400C", ncl="empty.ncl",
                    tiles=["PB25:PIC_B_DUMMY_VIQ_VREF"]), [("BDLLDEL0", "R31C25"), ("BDLLDEL1", "R31C25")]),

        (FuzzConfig(job="LDLLDEL", family="MachXO3", device="LCMXO3LF-9400C", ncl="empty.ncl",
                    tiles=["CIB_R15C1:CIB_EBR0_END0_10K"]),  [("LDLLDEL1", "R15C0")]),
        (FuzzConfig(job="LDLLDEL", family="MachXO3", device="LCMXO3LF-9400C", ncl="empty.ncl",
                    tiles=["CIB_R22C1:CIB_EBR0_END0_DLL3"]), [("LDLLDEL0", "R15C0")]),
        (FuzzConfig(job="LDLLDEL", family="MachXO3", device="LCMXO3LF-9400C", ncl="empty.ncl",
                    tiles=["CIB_R8C1:CIB_EBR0_END0_DLL5"]),  [("LDLLDEL2", "R15C0")]),

        (FuzzConfig(job="RDLLDEL", family="MachXO3", device="LCMXO3LF-9400C", ncl="empty.ncl",
                    tiles=["CIB_R15C49:CIB_EBR2_END1_10K"]), [("RDLLDEL0", "R15C50")]),
       ]


def todecstr(x):
    res = 0
    for i in range(len(x)):
        if x[i]:
            res |= 1 << i
    return str(res)


def main():
    pytrellis.load_database("../../../../database")

    for job in jobs:
        cfg, locs = job
        cfg.setup()

        empty_bitfile = cfg.build_design(cfg.ncl, {})

        for loc, rc in locs:
            def get_substs(mode="DLLDELC", program={}):
                if mode == "NONE":
                    comment = "//"
                else:
                    comment = ""
                program = ",".join(["{}={}".format(k, v) for k, v in program.items()])

                return dict(site=loc, comment=comment, program=program)

            cfg.ncl = "dlldel.ncl"

            nonrouting.fuzz_enum_setting(cfg, "{}.MODE".format(loc), ["NONE", "DLLDELC"],
                                         lambda x: get_substs(mode=x, program=dict(DEL_ADJ="PLUS")), empty_bitfile, False)
            nonrouting.fuzz_enum_setting(cfg, "{}.DEL_ADJ".format(loc), ["PLUS", "MINUS"],
                                         lambda x: get_substs(
                                             program=dict(DEL_ADJ=x, DEL_VAL=(1 if x == "PLUS" else 127))),
                                         empty_bitfile)
            nonrouting.fuzz_word_setting(cfg, "{}.DEL_VAL".format(loc), 7,
                                         lambda x: get_substs(program=dict(DEL_VAL=todecstr(x))), empty_bitfile)

            idx = loc[-1]
            netlist = []
            netlist.append(("{}_CLKO{}_DLLDEL".format(rc, idx), "driver"))
            netlist.append(("{}_JCKI{}_DLLDEL".format(rc, idx), "sink"))
            netlist.append(("{}_JDQSDEL{}_DLLDEL".format(rc, idx), "sink"))
            netlist.append(("{}_DLLDEL{}".format(rc, idx), "sink"))
            netlist.append(("{}_JINCK{}".format(rc, idx), "sink"))
            netlist.append(("{}_JPADDI{}".format(rc, idx), "sink"))
            nets = [net[0] for net in netlist]
            override_dict = {net[0]: net[1] for net in netlist}

            cfg.ncl = "dlldel_routing.ncl"
            interconnect.fuzz_interconnect_with_netnames(config=cfg,      
                                                        netnames=nets,
                                                        netname_filter_union=False,
                                                        bidir=True,
                                                        nonlocal_prefix="9400_",
                                                        netdir_override=override_dict)

if __name__ == "__main__":
    main()
