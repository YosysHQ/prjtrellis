from collections import defaultdict
from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import interconnect

cfg = FuzzConfig(job="PCNTR", family="MachXO2", device="LCMXO2-1200HC", ncl="empty.ncl",
                  tiles=["PT4:CFG0", "PT5:CFG1", "PT6:CFG2", "PT7:CFG3", "PT8:PIC_T_DUMMY_OSC"])

rcfg = FuzzConfig(job="PCNTR", family="MachXO2", device="LCMXO2-1200HC", ncl="pcntr_routing.ncl",
                    tiles=["CIB_R1C4:CIB_CFG0"])

def get_substs(mode="PCNTR", program={}):
    if mode == "NONE":
        comment = "//"
    else:
        comment = ""
    program = ",".join(["{}={}".format(k, v) for k, v in program.items()])
    return dict( comment=comment, program=program)

def main():
    pytrellis.load_database("../../../database")

    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "pcntr.ncl"
    
    nonrouting.fuzz_enum_setting(cfg, "PCNTR.STDBYOPT", ["USER_CFG", "USER", "CFG"],
                                lambda x: get_substs(program=dict(STDBYOPT=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "PCNTR.WAKEUP", ["USER", "CFG"],
                                 lambda x: get_substs(program=dict(WAKEUP=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "PCNTR.TIMEOUT", ["BYPASS", "USER", "COUNTER"],
                                 lambda x: get_substs(program=dict(TIMEOUT=x)), empty_bitfile, False)

    nonrouting.fuzz_enum_setting(cfg, "PCNTR.POROFF", ["FALSE", "TRUE"],
                                 lambda x: get_substs(program=dict(POROFF=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "PCNTR.BGOFF", ["FALSE", "TRUE"],
                                 lambda x: get_substs(program=dict(BGOFF=x)), empty_bitfile, False)

    rcfg.setup()

    override_dict = { "R1C4_JCLRFLAG_PCNTR" :"sink",
                    "R1C4_JUSERSTDBY_PCNTR" : "sink",
                    "R1C4_JUSERTIMEOUT_PCNTR" :"sink",
                    "R1C4_CLK_PCNTR" : "sink",
                    "R1C4_CFGWAKE_PCNTR" : "sink",
                    "R1C4_CFGSTDBY_PCNTR" : "sink",
                    "R1C4_JSFLAG_PCNTR" : "driver",
                    "R1C4_JSTDBY_PCNTR" : "driver",
                    "R1C4_JSTOP_PCNTR" : "driver" }

    nets = [net for net in override_dict]

    interconnect.fuzz_interconnect_with_netnames(
        rcfg,
        nets,
        bidir=True,
        netdir_override=override_dict
    )

if __name__ == "__main__":
    main()









