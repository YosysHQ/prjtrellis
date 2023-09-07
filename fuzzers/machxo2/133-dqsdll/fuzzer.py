from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import interconnect

jobs = [(FuzzConfig(job="DQSDLL_R", family="MachXO2", device="LCMXO2-1200HC", ncl="empty.ncl",
                    tiles=["PT21:DQSDLL_R"]), "TDQSDLL"),
        (FuzzConfig(job="DQSDLL_L", family="MachXO2", device="LCMXO2-1200HC", ncl="empty.ncl",
                    tiles=["PB2:DQSDLL_L"]), "BDQSDLL"),
        ]


jobs_routing = [
        (FuzzConfig(job="DQSDLL_R", family="MachXO2", device="LCMXO2-1200HC", ncl="routing_1200.ncl",
                    tiles=["PT21:DQSDLL_R"]), "TDQSDLL", "R1C21", "1200_"),
        (FuzzConfig(job="DQSDLL_L", family="MachXO2", device="LCMXO2-1200HC", ncl="routing_1200.ncl",
                    tiles=["PB2:DQSDLL_L"]), "BDQSDLL", "R11C2", "1200_"),

        (FuzzConfig(job="DQSDLL_R", family="MachXO2", device="LCMXO2-2000HC", ncl="routing_2000.ncl",
                    tiles=["PT25:DQSDLL_R"]), "TDQSDLL", "R1C25", "2000_"),
        (FuzzConfig(job="DQSDLL_L", family="MachXO2", device="LCMXO2-2000HC", ncl="routing_2000.ncl",
                    tiles=["PB2:DQSDLL_L"]), "BDQSDLL", "R14C2", "2000_"),

        (FuzzConfig(job="DQSDLL_R", family="MachXO2", device="LCMXO2-4000HC", ncl="routing_4000.ncl",
                    tiles=["PT29:DQSDLL_R"]), "TDQSDLL", "R1C29", "4000_"),
        (FuzzConfig(job="DQSDLL_L", family="MachXO2", device="LCMXO2-4000HC", ncl="routing_4000.ncl",
                    tiles=["PB2:DQSDLL_L"]), "BDQSDLL", "R21C2", "4000_"),

        (FuzzConfig(job="DQSDLL_R", family="MachXO2", device="LCMXO2-7000HC", ncl="routing_7000.ncl",
                    tiles=["PT38:DQSDLL_R"]), "TDQSDLL", "R1C38", "7000_"),
        (FuzzConfig(job="DQSDLL_L", family="MachXO2", device="LCMXO2-7000HC", ncl="routing_7000.ncl",
                    tiles=["PB2:DQSDLL_L"]), "BDQSDLL", "R26C2", "7000_"),
        ]

def todecstr(x):
    res = 0
    for i in range(len(x)):
        if x[i]:
            res |= 1 << i
    return str(res)


def main():
    pytrellis.load_database("../../../database")

    for job in jobs:
        cfg, loc = job
        cfg.setup()

        def get_muxval(sig, val):
            if val == sig:
                return None
            elif val in ("0", "1"):
                return {sig: val}
            elif val == "INV":
                return {sig: "#INV"}
            else:
                assert False

        def get_substs(mode="DQSDLLC", program={}, muxes=None):
            if mode == "NONE":
                comment = "//"
            else:
                comment = ""
            program = ",".join(["{}={}".format(k, v) for k, v in program.items()])
            if muxes is not None:
                program += ":" + ",".join(["{}={}".format(k, v) for k, v in muxes.items()]) 
            return dict(site=loc, comment=comment, program=program)

        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "dqsdll.ncl"

        # ignored bits are from FORCE_MAX_DELAY
        nonrouting.fuzz_enum_setting(cfg, "{}.MODE".format(loc), ["NONE", "DQSDLLC"],
                                        lambda x: get_substs(mode=x, program=dict(DEL_ADJ="PLUS")), empty_bitfile, False,
                                        ignore_bits=([("PT21:DQSDLL_R", 5, 14), ("PB2:DQSDLL_L", 0, 14)]))
        nonrouting.fuzz_enum_setting(cfg, "{}.RST".format(loc), ["0", "1", "RST", "INV"], lambda x: get_substs(
                                            muxes=get_muxval("RST",x)), empty_bitfile,
                                            ignore_bits=([("PT21:DQSDLL_R", 5, 14), ("PB2:DQSDLL_L", 0, 14)]))

        nonrouting.fuzz_enum_setting(cfg, "{}.DEL_ADJ".format(loc), ["PLUS", "MINUS"],
                                        lambda x: get_substs(
                                            program=dict(DEL_ADJ=x, DEL_VAL=(1 if x == "PLUS" else 127))),
                                        empty_bitfile)
        nonrouting.fuzz_word_setting(cfg, "{}.DEL_VAL".format(loc), 7,
                                        lambda x: get_substs(program=dict(DEL_VAL=todecstr(x))), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.FORCE_MAX_DELAY".format(loc), ["NO", "YES"], lambda x: get_substs(
                                            program=dict(FORCE_MAX_DELAY=x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.GSR".format(loc), ["ENABLED", "DISABLED"], lambda x: get_substs(
                                            program=dict(GSR=x)), empty_bitfile)
        nonrouting.fuzz_enum_setting(cfg, "{}.LOCK_SENSITIVITY".format(loc), ["LOW", "HIGH"], lambda x: get_substs(
                                            program=dict(LOCK_SENSITIVITY=x)), empty_bitfile)

    for job in jobs_routing:
       cfg, loc, rc, prefix = job
       cfg.setup()

       side = loc[0]
       netlist = []
       netlist.append(("{}_{}ECLK0".format(rc, side), "sink"))
       netlist.append(("{}_{}ECLK1".format(rc, side), "sink"))
       netlist.append(("{}_CLK_DQSDLL".format(rc), "sink"))
       netlist.append(("{}_DQSDLLCLK".format(rc), "driver"))
       netlist.append(("{}_JDIVOSC_DQSDLLTEST".format(rc), "sink"))
       netlist.append(("{}_JDQSDEL_DQSDLL".format(rc), "driver"))
       netlist.append(("{}_JDQSDLLSCLK".format(rc), "driver"))
       netlist.append(("{}_JFREEZE_DQSDLL".format(rc), "sink"))
       netlist.append(("{}_JLOCK_DQSDLL".format(rc), "driver"))
       netlist.append(("{}_JRST_DQSDLL".format(rc), "sink"))
       netlist.append(("{}_JUDDCNTLN_DQSDLL".format(rc), "sink"))
       for i in range(7):
           netlist.append(("{}_JSDOUT{}_DQSDLLTEST".format(rc,i), "driver"))

       nets = [net[0] for net in netlist]
       override_dict = {net[0]: net[1] for net in netlist}

       interconnect.fuzz_interconnect_with_netnames(config=cfg,      
                                                   netnames=nets,
                                                   netname_filter_union=False,
                                                   bidir=True,
                                                   nonlocal_prefix=prefix,
                                                   netdir_override=override_dict)


if __name__ == "__main__":
    main()
